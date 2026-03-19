# Lab 04 — Real-World Compose

> **Prerequisites:** You should have completed [Lab 01 (Docker Basics)](../lab-01-docker-basics/), [Lab 02 (Building Images)](../lab-02-building-images/), and [Lab 03 (Docker Compose)](../lab-03-docker-compose/). You should be comfortable with Dockerfiles, multi-container apps, `docker compose up/down`, named volumes, and service networking.

---

## 🎯 What You'll Learn

- How to build a realistic multi-service architecture with Docker Compose
- How to use **Nginx as a reverse proxy** in front of a backend API
- How to manage configuration with **environment variables** and a `.env` file
- How to use **named volumes** for database persistence
- How services communicate over the internal Docker Compose network
- How to verify data persistence — and how to intentionally wipe it

---

## 🤔 Why This Lab?

In Labs 01–03 you learned the building blocks: running containers, building images, and composing two services together. But real applications are more complex:

- Users don't hit your Python app directly — a **reverse proxy** (like Nginx) sits in front.
- Your database credentials shouldn't be hardcoded — they live in **environment variables**.
- Your database data must survive restarts — that requires **persistent volumes**.
- Internal services shouldn't be exposed to the outside world — only the proxy is public.

This lab puts it all together. You'll deploy a **Task Manager** web application with three services working as a team.

---

## 🏗️ The App We're Building

A simple **Task Manager API** made of three services:

1. **`nginx`** — A reverse proxy that receives all external traffic on port 80 and forwards API requests to the Flask backend. This is the **only** service exposed to the host.
2. **`api`** — A Python Flask REST API that handles business logic (create and list tasks). It talks to the database but is **not** directly accessible from outside — only Nginx can reach it.
3. **`db`** — A PostgreSQL database that stores all the tasks. Its data is saved to a **named volume** so it survives container restarts.

```
                    ┌──── Docker Compose Network ────────────────────────┐
                    │                                                    │
  curl localhost    │   ┌──────────┐     ┌──────────┐    ┌───────────┐   │
  ───────────────▶  │   │  nginx   │────▶│   api    │───▶│    db     │   │
       port 80      │   │  :80     │     │  :5000   │    │  :5432    │   │
                    │   └──────────┘     └──────────┘    └───────────┘   │
                    │        │                                  │        │
                    └────────┼──────────────────────────────────┼────────┘
                             │                                  │
                        port 80                           named volume
                        (host access)                     (data persistence)
```

**Key design decision:** The `api` and `db` services have **no ports mapped to the host**. They are only reachable from inside the Docker network. This is a security best practice — expose only what needs to be public.

---

## 📂 Step 1 — Explore the Project Structure

Before we start anything, take a look at what's in this directory:

```
lab-04-real-world-compose/
├── docker-compose.yml      ← Defines all 3 services and how they connect
├── .env                    ← Database credentials (shared by api + db)
├── api/
│   ├── Dockerfile          ← Builds the Flask API image
│   ├── app.py              ← The Flask application (REST API)
│   └── requirements.txt    ← Python dependencies (Flask + psycopg2)
└── nginx/
    ├── Dockerfile          ← Builds the Nginx image with our custom config
    └── nginx.conf          ← Reverse proxy configuration
```

| File | Purpose |
|---|---|
| `docker-compose.yml` | **The star of this lab** — orchestrates all three services |
| `.env` | Environment variables shared between the API and database |
| `api/app.py` | Flask REST API with endpoints for creating and listing tasks |
| `api/Dockerfile` | Builds the API image (same pattern as Labs 02 and 03) |
| `api/requirements.txt` | Python dependencies: Flask and psycopg2 (PostgreSQL driver) |
| `nginx/nginx.conf` | Nginx config that proxies `/api/*` requests to the Flask backend |
| `nginx/Dockerfile` | Copies our custom Nginx config into the official Nginx image |

Take a moment to open each file and read the comments. Everything is explained inline.

---

## 🔑 Step 2 — Understand the `.env` File

Open the `.env` file:

```
POSTGRES_DB=taskmanager
POSTGRES_USER=admin
POSTGRES_PASSWORD=secretpassword
```

This single file is the **source of truth** for database configuration. Both services that need database access reference it:

- **PostgreSQL (`db`)** reads these variables to automatically create the database and user on first startup. This is a feature of the official PostgreSQL Docker image.
- **Flask (`api`)** reads the same variables to build its database connection string.

In `docker-compose.yml`, both services reference the file with `env_file: .env`:

```yaml
# Both services load the same .env file:
api:
  env_file:
    - .env

db:
  env_file:
    - .env
```

> 💡 **Why use a `.env` file?**
> - **Single source of truth:** Change credentials in one place, both services pick them up.
> - **Separation of concerns:** Code doesn't contain secrets — they live in configuration.
> - **Security:** In a real project, you'd add `.env` to `.gitignore` so secrets never get committed to version control. We include it here for convenience.

---

## 🚀 Step 3 — Start the Application

Make sure you're in the `lab-04-real-world-compose/` directory, then run:

```bash
docker compose up -d --build
```

Let's break that down:

| Flag | Meaning |
|---|---|
| `up` | Create and start all services |
| `-d` | Detached mode (run in the background) |
| `--build` | Force a rebuild of images before starting (useful when you've changed code) |

You should see output like:

```
[+] Building 12.3s (15/15) FINISHED
...
[+] Running 4/4
 ✔ Network lab-04-real-world-compose_default      Created
 ✔ Container lab-04-real-world-compose-db-1       Started
 ✔ Container lab-04-real-world-compose-api-1      Started
 ✔ Container lab-04-real-world-compose-nginx-1    Started
```

Docker Compose just:

1. Built two custom images (`api` and `nginx`) from their Dockerfiles
2. Pulled the `postgres:16-alpine` image from Docker Hub
3. Created a private network so the three containers can talk to each other
4. Created a named volume for PostgreSQL data
5. Started all three containers in the correct order (`db` → `api` → `nginx`)

### Verify everything is running

```bash
docker compose ps
```

✅ **Expected output:**

```
NAME                                  IMAGE                                COMMAND                  SERVICE   CREATED          STATUS          PORTS
lab-04-real-world-compose-db-1        postgres:16-alpine                   "docker-entrypoint.s…"   db        30 seconds ago   Up 29 seconds   5432/tcp
lab-04-real-world-compose-api-1       lab-04-real-world-compose-api        "python app.py"          api       30 seconds ago   Up 29 seconds   5000/tcp
lab-04-real-world-compose-nginx-1     lab-04-real-world-compose-nginx      "/docker-entrypoint.…"   nginx     30 seconds ago   Up 28 seconds   0.0.0.0:80->80/tcp
```

Notice the **PORTS** column:

- `nginx` has `0.0.0.0:80->80/tcp` — it's accessible from the host on port 80 ✅
- `api` has `5000/tcp` — the port is exposed inside the network only, **not** mapped to the host 🔒
- `db` has `5432/tcp` — same, internal only 🔒

---

## ✅ Step 4 — Test the Application

### Test that Nginx is running

```bash
curl localhost
```

✅ **Expected output:**

```
Welcome to the Task Manager! 🚀

Available endpoints:
  GET  /api/tasks   — List all tasks
  POST /api/tasks   — Create a task
  GET  /api/health  — Health check
```

This response comes from Nginx's root `/` location. It proves Nginx is up and listening on port 80.

### Test the health endpoint (Nginx → Flask → PostgreSQL)

```bash
curl localhost/api/health
```

✅ **Expected output:**

```json
{"database":"connected","status":"healthy"}
```

This response traveled through the **entire stack**:

1. Your `curl` command hit **Nginx** on port 80
2. Nginx matched the `/api/` prefix and forwarded the request to **Flask** at `api:5000`
3. Flask connected to **PostgreSQL** at `db:5432`, ran a test query, and confirmed it's connected
4. The response traveled back: Flask → Nginx → your terminal

🎉 **All three services are talking to each other!**

### Test listing tasks (should be empty)

```bash
curl localhost/api/tasks
```

✅ **Expected output:**

```json
[]
```

No tasks yet — the database is empty. Let's fix that.

---

## 📝 Step 5 — Create Some Tasks

Use `curl -X POST` to create tasks via the API:

```bash
curl -X POST localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Docker basics"}'
```

✅ **Expected output:**

```json
{"done":false,"id":1,"title":"Learn Docker basics"}
```

The API created the task in PostgreSQL and returned it with an auto-generated `id`. Let's add a few more:

```bash
curl -X POST localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Build custom images"}'

curl -X POST localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Master Docker Compose"}'

curl -X POST localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy a real-world app"}'
```

---

## 📋 Step 6 — List All Tasks

```bash
curl localhost/api/tasks
```

✅ **Expected output:**

```json
[
  {"done":false,"id":1,"title":"Learn Docker basics"},
  {"done":false,"id":2,"title":"Build custom images"},
  {"done":false,"id":3,"title":"Master Docker Compose"},
  {"done":false,"id":4,"title":"Deploy a real-world app"}
]
```

All four tasks are stored in PostgreSQL and returned through the full Nginx → Flask → PostgreSQL pipeline. 🎉

> 💡 **Try the error case too:**
>
> ```bash
> curl -X POST localhost/api/tasks \
>   -H "Content-Type: application/json" \
>   -d '{"title": ""}'
> ```
>
> Expected: `{"error":"A 'title' field is required."}` with HTTP status 400.

---

## 🔄 Step 7 — Prove Data Persists Across Restarts

This is one of the most important concepts in this lab. Let's stop everything and start it again:

```bash
docker compose down
```

✅ **Expected output:**

```
[+] Running 4/4
 ✔ Container lab-04-real-world-compose-nginx-1  Removed
 ✔ Container lab-04-real-world-compose-api-1    Removed
 ✔ Container lab-04-real-world-compose-db-1     Removed
 ✔ Network lab-04-real-world-compose_default    Removed
```

The containers and network are gone. But notice — **no volume was removed**.

Now start everything again:

```bash
docker compose up -d
```

And check our tasks:

```bash
curl localhost/api/tasks
```

✅ **Expected output — the data is still there!**

```json
[
  {"done":false,"id":1,"title":"Learn Docker basics"},
  {"done":false,"id":2,"title":"Build custom images"},
  {"done":false,"id":3,"title":"Master Docker Compose"},
  {"done":false,"id":4,"title":"Deploy a real-world app"}
]
```

> 💡 **Why did the data survive?** Because `docker compose down` removes containers and networks but **preserves named volumes**. The PostgreSQL data lives in the `postgres-data` volume, which is still on disk. When the new `db` container starts, it reattaches to the same volume and finds all the data waiting.

You can verify the volume still exists:

```bash
docker volume ls | grep postgres
```

✅ **Expected output:**

```
local     lab-04-real-world-compose_postgres-data
```

---

## 🗑️ Step 8 — Remove Everything (Including Data)

Now let's see what happens when we **also** remove volumes:

```bash
docker compose down -v
```

✅ **Expected output:**

```
[+] Running 5/5
 ✔ Container lab-04-real-world-compose-nginx-1         Removed
 ✔ Container lab-04-real-world-compose-api-1           Removed
 ✔ Container lab-04-real-world-compose-db-1            Removed
 ✔ Volume lab-04-real-world-compose_postgres-data      Removed
 ✔ Network lab-04-real-world-compose_default           Removed
```

Notice the extra line: **Volume ... Removed**. The database data is gone.

Start fresh and verify:

```bash
docker compose up -d
```

Wait a couple of seconds for PostgreSQL to initialize, then:

```bash
curl localhost/api/tasks
```

✅ **Expected output — the data is gone:**

```json
[]
```

The database was created from scratch because the volume was deleted. This is a clean slate.

> 💡 **Key takeaway:**
> - `docker compose down` → containers gone, **data preserved** ✅
> - `docker compose down -v` → containers gone, **data gone** 🗑️
>
> In practice, you almost never want `-v` in production. But it's invaluable during development when you want to reset to a clean state.

---

## 📜 Bonus — View Logs

You can follow what's happening inside each service:

### All services

```bash
docker compose logs
```

### Specific service

```bash
docker compose logs api
```

### Follow logs in real time

```bash
docker compose logs -f api
```

Then in another terminal, run some `curl` commands — you'll see the Flask requests appear live. Press `Ctrl+C` to stop following.

> 💡 **Tip:** The Flask API prints startup messages like `✅ Database is ready` and `🚀 Task Manager API is running`. Check `docker compose logs api` if something isn't working — the retry messages will tell you if the database connection is having issues.

---

## 🧹 Final Cleanup

When you're done with this lab:

```bash
docker compose down -v
```

To also remove the built images:

```bash
docker compose down -v --rmi all
```

---

## 📋 Quick Reference — Docker Compose Commands

| Command | Purpose |
|---|---|
| `docker compose up -d --build` | Build images and start all services in the background |
| `docker compose ps` | List running services in this project |
| `docker compose logs` | View combined logs from all services |
| `docker compose logs <service>` | View logs for a specific service |
| `docker compose logs -f` | Follow logs in real time |
| `docker compose down` | Stop and remove containers + network (keeps volumes) |
| `docker compose down -v` | Same, but also remove named volumes (deletes data!) |
| `docker compose down -v --rmi all` | Same, but also remove built images |

---

## 🧠 What You've Learned Across All Labs

Congratulations — you've completed the entire Docker hands-on lab series! 🎉 Here's a summary of everything you've learned:

### Lab 01 — Docker Basics
- Pulling images from Docker Hub
- Running containers (interactive, detached, with port mapping)
- Listing, stopping, and removing containers
- Cleaning up with `docker system prune`

### Lab 02 — Building Images
- Writing a Dockerfile from scratch
- Building images with `docker build`
- Understanding layers and caching
- Tagging images with meaningful version numbers

### Lab 03 — Docker Compose
- Defining multi-container apps in `docker-compose.yml`
- Service-to-service networking (containers talk by name)
- Named volumes for data persistence
- Managing the app lifecycle with `docker compose up/down`

### Lab 04 — Real-World Compose (This Lab)
- Realistic multi-service architecture (proxy + backend + database)
- Nginx as a reverse proxy (only public entry point)
- Environment variables and `.env` files for configuration
- Keeping internal services private (no host port mapping)
- Data persistence across restarts with named volumes
- The difference between `down` (keep data) and `down -v` (lose data)

---

## 🚀 Where to Go from Here

You now have a solid foundation in Docker and Docker Compose. Here are some ideas for further exploration:

- **Add a frontend** — Build a simple HTML/JS app, serve it from Nginx, and have it call the API.
- **Add health checks** — Use Compose's `healthcheck` directive so `depends_on` waits for services to be truly ready (not just started).
- **Try Docker networking** — Create custom networks to isolate services (e.g., Nginx can only talk to the API, not directly to the database).
- **Explore Docker in CI/CD** — Use Docker to build and test your applications in Jenkins pipelines.
- **Learn about orchestration** — Look into Kubernetes or Docker Swarm for running containers at scale across multiple machines.

Happy containerizing! 🐳
