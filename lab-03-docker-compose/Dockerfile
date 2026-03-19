# ============================================================
# Dockerfile for a Flask + Redis counter application
# Used by Docker Compose in this lab to build the "web" service
# ============================================================

# FROM — Start from an official Python base image.
# "3.11-slim" is a lightweight variant that keeps the image small.
FROM python:3.11-slim

# WORKDIR — Set the working directory inside the container.
# All subsequent commands (COPY, RUN, CMD) will run from /app.
# If the directory doesn't exist, Docker creates it automatically.
WORKDIR /app

# COPY — Copy the requirements file into the container first.
# We copy this separately (before the rest of the code) so Docker
# can cache the dependency-installation layer. If requirements.txt
# hasn't changed, Docker skips the next RUN step on rebuilds.
COPY requirements.txt .

# RUN — Execute a command during the image build.
# Here we install the Python dependencies listed in requirements.txt.
# This lab needs Flask (the web framework) and redis (the Python client
# for talking to the Redis database).
# --no-cache-dir tells pip not to store downloaded packages, keeping
# the image smaller.
RUN pip install --no-cache-dir -r requirements.txt

# COPY — Now copy the rest of the application code into the container.
# The "." on the left  = everything in the build context (this folder).
# The "." on the right = the WORKDIR inside the container (/app).
COPY . .

# EXPOSE — Document that the container listens on port 5000.
# This doesn't actually publish the port; it serves as documentation
# for anyone reading the Dockerfile. The actual port mapping is
# configured in docker-compose.yml under the "ports" section.
EXPOSE 5000

# CMD — The default command that runs when the container starts.
# We use the "exec form" (JSON array) so the process receives
# signals correctly (e.g., SIGTERM for graceful shutdown).
CMD ["python", "app.py"]
