# Docker & Docker Compose — Hands-On Lab 🐳

Welcome! This repository contains a hands-on lab designed to take you from zero Docker experience to deploying a full multi-service application with Docker Compose.

All the code is provided — you just need to follow the instructions in each lab folder.

---

## Prerequisites

### Install Docker

The easiest way to install Docker is using the [ed2k](https://github.com/Ebury/ed2k) repository and its `local-setup.sh` script.

1. Clone the ed2k repository (if you haven't already):

    ```bash
    cd ed2k
    ```

2. Run the local setup script:

    ```bash
    chmod +x ./local-setup.sh
    ./local-setup.sh
    ```

    The script will check your environment, install Docker and Docker Compose if needed, and configure everything for you.

3. **Important:** If this is your first time installing Docker, you may need to **log out and log back in** (or restart your laptop) for the group permissions to take effect. You'll know this is needed if you see an error like:

    ```
    permission denied while trying to connect to the Docker daemon socket...
    ```

4. Verify the installation:

    ```bash
    docker --version
    docker compose version
    ```

    You should see version numbers for both. If so, you're ready to go!

> **Note:** If the ed2k script doesn't work for your setup, you can also install Docker manually following the [official documentation](https://docs.docker.com/engine/install/).

---

## Clone This Repository

```bash
git clone git@github.com:victorramosEbury/docker-lab.git
cd docker-lab
```

---

## Lab Structure

The lab is divided into 4 progressive exercises. **Do them in order** — each one builds on concepts from the previous lab.

```
docker-lab/
├── lab-01-docker-basics/          # Your first containers
├── lab-02-building-images/        # Write a Dockerfile, build an image
├── lab-03-docker-compose/         # Multi-container app with Compose
└── lab-04-real-world-compose/     # Full architecture: Nginx + API + Database
```

---

## How to Proceed

Each lab has its own `README.md` with step-by-step instructions. Navigate to the lab folder and follow the guide.

### Lab 01 — Docker Basics

```bash
cd lab-01-docker-basics
```

Learn the fundamentals: run containers, inspect them, stop them, remove them. Get comfortable with the Docker CLI.

### Lab 02 — Building Images

```bash
cd lab-02-building-images
```

Write a Dockerfile, build a custom image, and understand how layers and caching work.

### Lab 03 — Docker Compose

```bash
cd lab-03-docker-compose
```

Define and run a multi-container application (Flask + Redis) with a single `docker compose up` command.

### Lab 04 — Real-World Compose

```bash
cd lab-04-real-world-compose
```

Deploy a realistic 3-service architecture: Nginx reverse proxy → Flask REST API → PostgreSQL database. Learn about environment variables, named volumes, and service isolation.

---

## Tips

- **Read the README in each lab**, don't just copy-paste commands. The explanations are where the learning happens.
- Each step includes **expected output** so you can verify everything is working correctly.
- If something goes wrong, `docker compose down -v` gives you a clean slate to start over.
- If a port is already in use, try changing the host port (e.g., `-p 9090:80` instead of `-p 8080:80`).

---

## Useful Commands Cheat Sheet

| Command | What it does |
|---|---|
| `docker run <image>` | Run a container from an image |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker stop <id>` | Stop a running container |
| `docker rm <id>` | Remove a stopped container |
| `docker images` | List local images |
| `docker build -t <name> .` | Build an image from a Dockerfile |
| `docker compose up` | Start all services (foreground) |
| `docker compose up -d` | Start all services (background) |
| `docker compose down` | Stop and remove containers (keep data) |
| `docker compose down -v` | Stop and remove everything including data |
| `docker compose ps` | List running services |
| `docker compose logs -f` | Follow logs in real time |
| `docker system prune` | Clean up unused resources |

---

Happy learning! 🐳
