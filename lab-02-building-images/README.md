# Lab 02 — Building Docker Images

> **Prerequisites:** You should have completed [Lab 01 (Docker Basics)](../lab-01-docker-basics/) and be comfortable with `docker run`, `docker ps`, `docker stop`, and `docker rm`.

---

## 🎯 What You'll Learn

- What a Dockerfile is and why you need one
- How to write a Dockerfile from scratch
- How to build a Docker image from your own code
- How to run and test your custom image
- How Docker layer caching works (and why rebuilds are fast)
- How to tag images with meaningful names and versions

---

## 📦 What Is a Dockerfile?

A **Dockerfile** is a plain text file that contains a set of instructions telling Docker **how to build an image**. Think of it like a recipe:

- Each instruction adds a new **layer** to the image.
- Docker reads the file from top to bottom and executes each instruction in order.
- The result is a portable, reproducible image you can run anywhere Docker is installed.

The Dockerfile in this lab directory builds a tiny Python Flask web application. Let's walk through it step by step.

---

## 🔍 Understanding the Dockerfile

Open the `Dockerfile` in this directory. Here's what each instruction does:

| Instruction | What It Does |
|---|---|
| `FROM python:3.11-slim` | Sets the **base image**. We start from an official Python image so we don't have to install Python ourselves. The `slim` variant is smaller than the full image. |
| `WORKDIR /app` | Sets the **working directory** inside the container. All subsequent commands run from `/app`. If the directory doesn't exist, Docker creates it. |
| `COPY requirements.txt .` | Copies `requirements.txt` from your machine into the container's `/app` directory. We copy this **first** to take advantage of layer caching (more on that below). |
| `RUN pip install --no-cache-dir -r requirements.txt` | Runs a command **during the build**. Here it installs the Python dependencies. The `--no-cache-dir` flag keeps the image smaller. |
| `COPY . .` | Copies the **rest of your project files** into the container. |
| `EXPOSE 5000` | Documents that the container listens on port 5000. This is informational — you still need `-p` when running. |
| `CMD ["python", "app.py"]` | Sets the **default command** that runs when the container starts. |

---

## 🏗️ Step 1 — Build the Image

Make sure you're in the `lab-02-building-images/` directory (where the `Dockerfile` lives), then run:

```bash
docker build -t my-flask-app .
```

Let's break that down:

| Part | Meaning |
|---|---|
| `docker build` | Tell Docker to build an image |
| `-t my-flask-app` | **Tag** (name) the image as `my-flask-app` |
| `.` | Use the current directory as the **build context** (where Docker looks for the Dockerfile and your files) |

You should see output like this:

```
Step 1/7 : FROM python:3.11-slim
 ---> a3d28b7a2f5e
Step 2/7 : WORKDIR /app
 ---> Running in 7c1e2f3a4b5c
...
Successfully built 9f8e7d6c5b4a
Successfully tagged my-flask-app:latest
```

Each step corresponds to one instruction in the Dockerfile.

### Verify your image exists

```bash
docker images my-flask-app
```

You should see something like:

```
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
my-flask-app   latest    9f8e7d6c5b4a   10 seconds ago   135MB
```

---

## 🚀 Step 2 — Run the Image

Start a container from your new image:

```bash
docker run -d -p 5000:5000 --name flask-lab my-flask-app
```

| Flag | Meaning |
|---|---|
| `-d` | Run in **detached** mode (in the background) |
| `-p 5000:5000` | Map port 5000 on your machine to port 5000 in the container |
| `--name flask-lab` | Give the container a friendly name |
| `my-flask-app` | The image to run |

---

## ✅ Step 3 — Test It

### Test the main endpoint

```bash
curl localhost:5000
```

Expected output:

```
Hello from Docker! 🐳
```

### Test the health endpoint

```bash
curl localhost:5000/health
```

Expected output:

```json
{"status":"healthy"}
```

🎉 **Congratulations!** You just built and ran your first custom Docker image!

---

## 🔎 Step 4 — View Build Layers

Every instruction in the Dockerfile creates a **layer**. You can inspect them with:

```bash
docker history my-flask-app
```

You'll see output like:

```
IMAGE          CREATED          CREATED BY                                      SIZE
9f8e7d6c5b4a   2 minutes ago   CMD ["python" "app.py"]                         0B
<missing>      2 minutes ago   EXPOSE map[5000/tcp:{}]                         0B
<missing>      2 minutes ago   COPY . .                                        512B
<missing>      2 minutes ago   RUN pip install --no-cache-dir -r requiremen…   12.4MB
<missing>      2 minutes ago   COPY requirements.txt .                         12B
<missing>      2 minutes ago   WORKDIR /app                                    0B
<missing>      3 weeks ago     /bin/sh -c #(nop) CMD ["python3"]               0B
...
```

**Key takeaway:** Layers are stacked on top of each other. The base image (`python:3.11-slim`) has its own layers at the bottom, and your Dockerfile instructions add layers on top.

---

## ♻️ Step 5 — Rebuild After a Code Change (Layer Caching)

Docker is smart about caching. If a layer hasn't changed, Docker reuses it instead of rebuilding it. Let's see this in action.

### 1. Edit the app

Open `app.py` and change the hello message:

```python
def hello():
    return "Hello from Docker! 🐳 (v2 — updated!)"
```

### 2. Rebuild the image

```bash
docker build -t my-flask-app .
```

Watch the output carefully. You'll see something like:

```
Step 1/7 : FROM python:3.11-slim
 ---> Using cache
Step 2/7 : WORKDIR /app
 ---> Using cache
Step 3/7 : COPY requirements.txt .
 ---> Using cache
Step 4/7 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Using cache
Step 5/7 : COPY . .
 ---> 3a2b1c4d5e6f        <-- This layer changed!
Step 6/7 : EXPOSE 5000
 ---> Running in ...
Step 7/7 : CMD ["python", "app.py"]
 ---> Running in ...
Successfully built ...
```

Notice that Steps 1–4 say **"Using cache"** — Docker didn't reinstall your Python dependencies because `requirements.txt` didn't change. Only Step 5 onwards was rebuilt because `app.py` changed.

> 💡 **This is why we copy `requirements.txt` before copying the rest of the code.** Dependencies change rarely, but code changes often. This ordering keeps rebuilds fast.

### 3. Run the updated image

First, stop and remove the old container:

```bash
docker stop flask-lab
docker rm flask-lab
```

Then start a new one:

```bash
docker run -d -p 5000:5000 --name flask-lab my-flask-app
```

Test it:

```bash
curl localhost:5000
```

You should see your updated message:

```
Hello from Docker! 🐳 (v2 — updated!)
```

---

## 🏷️ Step 6 — Tagging Images

So far, our image is tagged as `my-flask-app:latest` (Docker adds `:latest` by default). In practice, you should use **explicit version tags**.

### Tag with a version number

```bash
docker tag my-flask-app my-flask-app:1.0
```

### Tag with multiple tags

```bash
docker tag my-flask-app my-flask-app:v2
docker tag my-flask-app my-flask-app:stable
```

### View all tags for your image

```bash
docker images my-flask-app
```

Output:

```
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
my-flask-app   1.0       9f8e7d6c5b4a   5 minutes ago    135MB
my-flask-app   latest    9f8e7d6c5b4a   5 minutes ago    135MB
my-flask-app   stable    9f8e7d6c5b4a   5 minutes ago    135MB
my-flask-app   v2        9f8e7d6c5b4a   5 minutes ago    135MB
```

Notice they all share the **same Image ID** — tags are just labels pointing to the same image.

> 💡 **Tip:** Avoid relying on `latest` in production. Always use explicit version tags so you know exactly what's deployed.

---

## 🧹 Cleanup

When you're done experimenting, clean up:

```bash
# Stop and remove the container
docker stop flask-lab
docker rm flask-lab

# Remove the images (all tags)
docker rmi my-flask-app:1.0 my-flask-app:v2 my-flask-app:stable my-flask-app:latest
```

---

## 📋 Quick Reference — Dockerfile Instructions Used

| Instruction | Purpose | Example |
|---|---|---|
| `FROM` | Set the base image | `FROM python:3.11-slim` |
| `WORKDIR` | Set the working directory inside the container | `WORKDIR /app` |
| `COPY` | Copy files from host to container | `COPY requirements.txt .` |
| `RUN` | Execute a command during the build | `RUN pip install -r requirements.txt` |
| `EXPOSE` | Document which port the container listens on | `EXPOSE 5000` |
| `CMD` | Set the default command when the container starts | `CMD ["python", "app.py"]` |

---

## 📋 Quick Reference — Docker CLI Commands Used

| Command | Purpose |
|---|---|
| `docker build -t <name> .` | Build an image from a Dockerfile |
| `docker images <name>` | List images (optionally filtered by name) |
| `docker run -d -p <host>:<container> <image>` | Run a container in the background with port mapping |
| `docker history <image>` | Show the layers of an image |
| `docker tag <image> <image>:<tag>` | Add a tag to an image |
| `docker rmi <image>` | Remove an image |

---

## ⏭️ What's Next?

You now know how to build, run, and tag your own Docker images. In [Lab 03 (Docker Compose)](../lab-03-docker-compose/), you'll learn how to run **multiple containers together** — a Flask API and a Redis database — using a single `docker-compose.yml` file.