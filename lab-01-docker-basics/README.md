# Lab 01 – Docker Basics 🐳

Welcome to your very first Docker lab! By the end of this exercise you'll be comfortable pulling images, running containers, and cleaning up after yourself. Let's dive in.

---

## What is Docker?

Docker is a tool that lets you package an application and all its dependencies into a lightweight, portable unit called a **container**. Containers run the same way on every machine, which eliminates the classic "it works on my machine" problem. Think of it as a tiny, isolated environment that starts in seconds.

---

## 1. Running Your First Container

Let's start with the simplest possible container — `hello-world`. It prints a welcome message and exits.

```bash
docker run hello-world
```

✅ **Expected output** (trimmed):

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

**What just happened?**

1. Docker looked for the `hello-world` image on your machine.
2. It didn't find it, so it **pulled** (downloaded) it from Docker Hub.
3. It created a container from that image, ran it, and printed the message.
4. The container exited automatically because its job was done.

---

## 2. Running an Interactive Container

Now let's run something more interesting — a full Ubuntu environment that you can type commands into.

```bash
docker run -it ubuntu bash
```

| Flag | Meaning |
|------|---------|
| `-i` | Keep STDIN open (interactive) |
| `-t` | Allocate a pseudo-TTY (gives you a terminal prompt) |

You should land inside the container with a prompt that looks something like:

```
root@a1b2c3d4e5f6:/#
```

Try a few commands inside the container:

```bash
whoami
cat /etc/os-release
ls /
```

When you're done exploring, type:

```bash
exit
```

This stops the container and brings you back to your host terminal.

---

## 3. Running a Detached Container

Interactive mode is great for experimenting, but most real-world containers run in the **background** (detached mode). Let's spin up an Nginx web server:

```bash
docker run -d -p 8080:80 nginx
```

| Flag | Meaning |
|------|---------|
| `-d` | Run in detached mode (background) |
| `-p 8080:80` | Map port **8080** on your host to port **80** inside the container |

✅ **Expected output** — a long container ID:

```
a3f8e7d612b4c9f01e56d7a8b3c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2
```

Now verify the web server is running:

```bash
curl localhost:8080
```

✅ **Expected output** (trimmed):

```html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

If you see the Nginx welcome page HTML, the container is up and serving traffic. You can also open <http://localhost:8080> in your browser.

---

## 4. Listing Containers

### See running containers

```bash
docker ps
```

✅ **Expected output:**

```
CONTAINER ID   IMAGE   COMMAND                  CREATED          STATUS          PORTS                  NAMES
a3f8e7d612b4   nginx   "/docker-entrypoint.…"   2 minutes ago    Up 2 minutes    0.0.0.0:8080->80/tcp   gracious_darwin
```

### See all containers (including stopped ones)

```bash
docker ps -a
```

This will also show the `hello-world` and `ubuntu` containers that already exited. Notice the **STATUS** column — it tells you whether a container is `Up` or `Exited`.

---

## 5. Stopping and Removing Containers

### Stop a running container

Use the container ID (or name) from `docker ps`:

```bash
docker stop a3f8e7d612b4
```

> 💡 **Tip:** You don't need to type the full ID. The first 3-4 characters are usually enough, e.g. `docker stop a3f8`.

Verify it stopped:

```bash
docker ps
```

The Nginx container should no longer appear (but it will still show up in `docker ps -a` with status `Exited`).

### Remove a stopped container

```bash
docker rm a3f8e7d612b4
```

✅ **Expected output:**

```
a3f8e7d612b4
```

You can also stop **and** remove in one step with the force flag:

```bash
docker rm -f <container_id>
```

---

## 6. Listing and Removing Images

Every container is created from an **image**. Even after you remove all containers, the images stay on disk.

### List all images

```bash
docker images
```

✅ **Expected output:**

```
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         latest    a8758716bb6a   2 weeks ago    187MB
ubuntu        latest    35a88802559d   3 weeks ago    78.1MB
hello-world   latest    d2c94e258dcb   9 months ago   13.3kB
```

### Remove an image

```bash
docker rmi hello-world
```

> ⚠️ You can only remove an image if no containers (running **or** stopped) are using it. Remove the containers first.

---

## 7. Cleanup – Start Fresh 🧹

After experimenting you may have a bunch of stopped containers, unused images, and dangling resources. Docker has a handy command to clean it all up at once:

⚠️ THIS WILL REMOVE ALSO OTHER CONTAINERS RUNNING PRIOR TO THIS LAB

```bash
docker system prune
```

You'll be prompted to confirm:

```
WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all dangling images
  - all dangling build cache

Are you sure you want to continue? [y/N] n
```

If you type `y` and press Enter. Docker will reclaim the disk space and show you how much was freed.

> 💡 **Tip:** Add `-a` to also remove **all** unused images (not just dangling ones):
>
> ```bash
> docker system prune -a
> ```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker run <image>` | Create and start a container from an image |
| `docker run -it <image> bash` | Run interactively with a shell |
| `docker run -d -p HOST:CONTAINER <image>` | Run detached with port mapping |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker stop <id>` | Stop a running container |
| `docker rm <id>` | Remove a stopped container |
| `docker images` | List downloaded images |
| `docker rmi <image>` | Remove an image |
| `docker system prune` | Clean up unused resources |

---

## You Did It! 🎉

You just ran your first containers, served a web page with Nginx, and learned how to clean up. These commands form the foundation of everything you'll do with Docker going forward.

When you're ready, move on to the next lab where we'll build our own custom Docker image with a `Dockerfile`.
