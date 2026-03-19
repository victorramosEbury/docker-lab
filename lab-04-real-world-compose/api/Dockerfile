# ============================================================
# Dockerfile for the Task Manager Flask API
# ============================================================
# This builds the "api" service for Lab 04. It packages a small
# Flask application that talks to PostgreSQL and serves a REST
# API for managing tasks.
#
# The pattern here is the same as Labs 02 and 03:
#   1. Start from a slim Python base image
#   2. Copy and install dependencies first (for layer caching)
#   3. Copy the application code
#   4. Define the default startup command
# ============================================================

# FROM — Start from an official Python base image.
# "3.11-slim" is a lightweight Debian-based variant that keeps
# the image small (~120 MB vs ~900 MB for the full image).
FROM python:3.11-slim

# WORKDIR — Set the working directory inside the container.
# All subsequent commands (COPY, RUN, CMD) will run from /app.
# If the directory doesn't exist, Docker creates it automatically.
WORKDIR /app

# COPY — Copy the requirements file into the container first.
# We copy this separately (before the rest of the code) so Docker
# can cache the dependency-installation layer. If requirements.txt
# hasn't changed, Docker skips the next RUN step on rebuilds —
# saving time because pip install doesn't need to run again.
COPY requirements.txt .

# RUN — Install the Python dependencies during the image build.
# This lab needs:
#   - Flask          (the web framework)
#   - psycopg2-binary (PostgreSQL database driver)
# --no-cache-dir tells pip not to store downloaded packages,
# keeping the final image smaller.
RUN pip install --no-cache-dir -r requirements.txt

# COPY — Now copy the rest of the application code into the
# container. Because this layer comes AFTER the pip install
# layer, changing app.py won't trigger a full reinstall of
# dependencies on rebuild.
COPY . .

# EXPOSE — Document that the container listens on port 5000.
# This doesn't actually publish the port — it's metadata for
# anyone reading the Dockerfile. In this lab, the API is NOT
# exposed to the host directly; only the Nginx reverse proxy
# can reach it over the internal Docker Compose network.
EXPOSE 5000

# CMD — The default command that runs when the container starts.
# We use the "exec form" (JSON array) so the Python process
# receives OS signals correctly (e.g., SIGTERM for graceful
# shutdown when you run "docker compose down").
CMD ["python", "app.py"]
