# Lab 03 — Docker Compose

> **Prerequisites:** You should have completed [Lab 01 (Docker Basics)](../lab-01-docker-basics/) and [Lab 02 (Building Images)](../lab-02-building-images/). You should be comfortable with `docker run`, `docker build`, Dockerfiles, and port mapping.

---

## 🎯 What You'll Learn

- What Docker Compose is and why you need it
- How to define a multi-container application in a `docker-compose.yml` file
- How to start, stop, and manage multiple containers with a single command
- How Docker Compose networking lets containers talk to each other by name
- How to use named volumes for data persistence

---

## 🤔 What Is Docker Compose?

In the previous labs you ran **one container at a time**. But real-world applications almost always involve **multiple services** working together — a web server, a database, a cache, a message queue, etc.

Imagine having to run each of those containers manually, remembering all the flags, ports, volumes, and network settings every time. That would get painful fast.

**Docker Compose** solves this. It lets you define your entire multi-container application in a single YAML file (`docker-compose.yml`) and manage it with simple commands:

| Without Compose | With Compose |
|---|---|
| Run each container separately with long `docker run` commands | Define everything in one file, run `docker compose up` |
| Manually create networks so containers can talk to each other | Compose creates a shared network automatically |
| Easy to forget a flag or misconfigure a port | Configuration is version-controlled and repeatable |
| Stop and remove each container one by one | `docker compose down` cleans up everything |

---

## 🏗️ The App We're Building

We're going to run a small application made of **two services**:

1. **`web`** — A Python Flask API that says hello and counts page visits.
2. **`redis`** — A Redis key-value store that keeps track of the visit counter.

Every time you visit the web page, Flask asks Redis to increment a counter and displays the result. Simple, but it demonstrates the core Compose concepts: multiple services, networking, and volumes.

```
┌─────────────────────────────────────────────┐
│           Docker Compose Network            │
│                                             │
│   ┌───────────┐       ┌───────────────┐     │
│   │    web    │──────▶│     redis     │     │
│   │  (Flask)  │       │  (Redis 7)    │     │
│   │  :5000    │       │  :6379        │     │
│   └───────────┘       └───────────────┘     │
│        │                      │             │
│        │                      │             │
└────────┼──────────────────────┼─────────────┘
         │                      │
    port 5000              named volume
    (host access)          (data persistence)
```

---

## 📂 Files in This Lab

Before we start, take a look at what's in this directory:

| File | Purpose |
|---|---|
| `app.py` | The Flask application (Python code) |
| `requirements.txt` | Python dependencies (Flask and Redis client) |
| `Dockerfile` | Instructions to build the `web` service image |
| `docker-compose.yml` | **The star of this lab** — defines both services and how they connect |
| `README.md` | This file |

---

## 🔍 Step 1 — Understand the `docker-compose.yml`

Open `docker-compose.yml` in your editor. Let's walk through each section:

```yaml
# ---- Services ----
# Each service becomes a container when you run "docker compose up".

services:

  web:
    build: .                    # Build an image from the Dockerfile in this directory
    ports:
      - "5000:5000"             # Map host port 5000 → container port 5000
    depends_on:
      - redis                   # Start redis before web

  redis:
    image: redis:7-alpine       # Use a pre-built image from Docker Hub
    volumes:
      - redis-data:/data        # Persist Redis data to a named volume

# ---- Volumes ----
# Named volumes survive "docker compose down" (but not "docker compose down -v").

volumes:
  redis-data:
```

Here's a breakdown of the key concepts:

| Concept | What It Does |
|---|---|
| `services` | A list of containers that make up your app. Each service has a name (`web`, `redis`) that doubles as its **hostname** on the network. |
| `build: .` | Tells Compose to build an image from the `Dockerfile` in the current directory, instead of pulling one from Docker Hub. |
| `image: redis:7-alpine` | Tells Compose to pull and use this existing image directly. |
| `ports` | Maps a port on your host machine to a port inside the container (same as `-p` in `docker run`). |
| `depends_on` | Controls startup order. Here, `redis` starts before `web`. Note: this only waits for the container to **start**, not for the service inside to be **ready**. |
| `volumes` | Maps a named volume to a path inside the container. Redis stores its data in `/data`, so we persist that. |

> 💡 **Key insight:** Docker Compose automatically creates a **network** for your app. The `web` container can reach Redis simply by using `redis` as the hostname (look at `app.py` — the Redis host is set to `"redis"`). No IP addresses needed!

---

## 🚀 Step 2 — Start the Application

Make sure you're in the `lab-03-docker-compose/` directory, then run:

```bash
docker compose up
```

This single command does **everything**:

1. Builds the image for the `web` service (from the Dockerfile)
2. Pulls the `redis:7-alpine` image from Docker Hub
3. Creates a network for the two containers
4. Creates the `redis-data` volume
5. Starts both containers

You'll see **interleaved logs** from both services in your terminal:

```
[+] Running 2/2
 ✔ Container lab-03-docker-compose-redis-1  Created
 ✔ Container lab-03-docker-compose-web-1    Created
Attaching to redis-1, web-1
redis-1  | * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis-1  | * Redis version=7.2.4, bits=64, commit=00000000, modified=0
redis-1  | * Running mode=standalone, port=6379.
web-1    |  * Serving Flask app 'app'
web-1    |  * Running on all addresses (0.0.0.0)
web-1    |  * Running on http://127.0.0.1:5000
web-1    |  * Running on http://172.18.0.3:5000
```

Notice how each line is prefixed with the service name (`redis-1`, `web-1`). This makes it easy to see which container produced which output.

> ⚠️ **The terminal is attached to the logs.** Press `Ctrl+C` to stop the containers. We'll learn about detached mode later.

---

## ✅ Step 3 — Test the Application

Open a **new terminal** (leave Compose running in the first one) and run:

```bash
curl localhost:5000
```

✅ **Expected output:**

```
Hello from Docker Compose! 🐳 This page has been visited 1 time(s).
```

Run it a few more times:

```bash
curl localhost:5000
curl localhost:5000
curl localhost:5000
```

✅ **Expected output:**

```
Hello from Docker Compose! 🐳 This page has been visited 2 time(s).
Hello from Docker Compose! 🐳 This page has been visited 3 time(s).
Hello from Docker Compose! 🐳 This page has been visited 4 time(s).
```

The counter increments every time! That's Flask talking to Redis behind the scenes.

### Test the health endpoint

```bash
curl localhost:5000/health
```

✅ **Expected output:**

```json
{"redis":"connected","status":"healthy"}
```

This confirms that the `web` container can successfully reach the `redis` container over the Compose network.

🎉 **You're running a multi-container application with a single command!**

---

## 📋 Step 4 — Check Running Services

In your second terminal, run:

```bash
docker compose ps
```

✅ **Expected output:**

```
NAME                              IMAGE                          COMMAND                  SERVICE   CREATED         STATUS         PORTS
lab-03-docker-compose-redis-1     redis:7-alpine                 "docker-entrypoint.s…"   redis     3 minutes ago   Up 3 minutes   6379/tcp
lab-03-docker-compose-web-1       lab-03-docker-compose-web      "python app.py"          web       3 minutes ago   Up 3 minutes   0.0.0.0:5000->5000/tcp
```

This is similar to `docker ps`, but scoped to only the services defined in your `docker-compose.yml`.

---

## 📜 Step 5 — View Logs

Even when running in the foreground, you'll want to know how to view logs for individual services.

### View all logs (from all services)

```bash
docker compose logs
```

This shows the combined logs from both `web` and `redis`, with service name prefixes.

### View logs for a specific service

```bash
docker compose logs web
```

This shows only the Flask logs.

### Follow logs in real time

```bash
docker compose logs -f web
```

This tails the logs for the `web` service. Try running `curl localhost:5000` in another terminal — you'll see the request appear in real time.

Press `Ctrl+C` to stop following.

> 💡 **Tip:** `docker compose logs -f` (without a service name) follows logs from **all** services.

---

## 🛑 Step 6 — Stop and Clean Up

Go back to the terminal where Compose is running and press `Ctrl+C`. You'll see:

```
Gracefully stopping... (press Ctrl+C again to force)
[+] Stopping 2/2
 ✔ Container lab-03-docker-compose-web-1    Stopped
 ✔ Container lab-03-docker-compose-redis-1  Stopped
```

The containers are stopped, but they still exist (along with the network and volume). To **remove** everything:

```bash
docker compose down
```

✅ **Expected output:**

```
[+] Running 3/3
 ✔ Container lab-03-docker-compose-web-1    Removed
 ✔ Container lab-03-docker-compose-redis-1  Removed
 ✔ Network lab-03-docker-compose_default    Removed
```

Notice that `docker compose down` removes the containers and the network, but **keeps the volume**. This means your Redis data (the visit counter) will survive!

---

## 🔄 Step 7 — Detached Mode

Running in the foreground is great for debugging, but in practice you'll usually want to run in the **background** (detached mode):

```bash
docker compose up -d
```

✅ **Expected output:**

```
[+] Running 3/3
 ✔ Network lab-03-docker-compose_default    Created
 ✔ Container lab-03-docker-compose-redis-1  Started
 ✔ Container lab-03-docker-compose-web-1    Started
```

Your terminal is free! The containers are running in the background. Verify:

```bash
docker compose ps
```

Test that the counter **persisted** from before (because the volume survived `docker compose down`):

```bash
curl localhost:5000
```

✅ **Expected output** (the counter continues where it left off!):

```
Hello from Docker Compose! 🐳 This page has been visited 5 time(s).
```

> 💡 **Why did the counter persist?** Because `docker compose down` removes containers and networks but **not** named volumes. The Redis data was saved in the `redis-data` volume.

---

## 🗑️ Step 8 — Remove Everything (Including Volumes)

When you want a completely clean slate, use the `-v` flag to also remove volumes:

```bash
docker compose down -v
```

✅ **Expected output:**

```
[+] Running 4/4
 ✔ Container lab-03-docker-compose-web-1    Removed
 ✔ Container lab-03-docker-compose-redis-1  Removed
 ✔ Volume lab-03-docker-compose_redis-data  Removed
 ✔ Network lab-03-docker-compose_default    Removed
```

Now start it again and check:

```bash
docker compose up -d
curl localhost:5000
```

✅ **Expected output:**

```
Hello from Docker Compose! 🐳 This page has been visited 1 time(s).
```

The counter is back to 1 — the volume (and all its data) was removed.

---

## 🧹 Final Cleanup

When you're done with this lab:

```bash
docker compose down -v
```

This removes all containers, networks, and volumes created by this Compose file.

To also remove the built image:

```bash
docker compose down -v --rmi all
```

---

## 📋 Quick Reference — Docker Compose Commands

| Command | Purpose |
|---|---|
| `docker compose up` | Build (if needed) and start all services in the foreground |
| `docker compose up -d` | Same, but in the background (detached mode) |
| `docker compose up --build` | Force a rebuild of images before starting |
| `docker compose ps` | List running services in this project |
| `docker compose logs` | View combined logs from all services |
| `docker compose logs <service>` | View logs for a specific service |
| `docker compose logs -f` | Follow logs in real time |
| `docker compose stop` | Stop all running containers (without removing them) |
| `docker compose down` | Stop and remove containers and networks |
| `docker compose down -v` | Same, but also remove named volumes |
| `docker compose down -v --rmi all` | Same, but also remove built images |

---

## 🧠 Key Takeaways

1. **Docker Compose lets you define multi-container apps in a single YAML file.** No more remembering long `docker run` commands.
2. **Services can reach each other by name.** Compose creates a network where `web` can connect to `redis` just by using `"redis"` as the hostname.
3. **Named volumes persist data across restarts.** Use `docker compose down -v` only when you want to delete the data.
4. **`depends_on` controls startup order**, but doesn't wait for a service to be "ready." Your app code should handle retries.
5. **Detached mode (`-d`)** is how you'll usually run Compose in practice.

---

## ⏭️ What's Next?

You now know how to orchestrate multiple containers with Docker Compose. You've seen services, networks, volumes, and all the essential Compose commands. In the next lab, we'll explore more advanced topics like environment variables, custom networks, and scaling services.
