# ============================================================
# Dockerfile for the Nginx Reverse Proxy
# ============================================================
# This builds the "nginx" service for Lab 04. It takes the
# official Nginx Alpine image and replaces the default config
# with our custom reverse proxy configuration that forwards
# requests to the Flask API backend.
#
# This is intentionally simple — just two lines! In a real
# project you might also COPY static files (HTML/CSS/JS) for
# a frontend, add SSL certificates, or install extra modules.
# ============================================================

# FROM — Start from the official Nginx image on Alpine Linux.
# Alpine is a tiny Linux distribution (~5 MB), which keeps the
# final image very small (~40 MB total with Nginx included).
FROM nginx:alpine

# COPY — Replace the default Nginx site configuration with our
# custom reverse proxy config. The default config lives at
# /etc/nginx/conf.d/default.conf inside the container. By
# overwriting it, Nginx will use our settings (proxy to Flask)
# instead of the default "Welcome to Nginx" page.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# EXPOSE — Document that the container listens on port 80.
# This is informational only; the actual port mapping is done
# in docker-compose.yml under the "ports" section.
EXPOSE 80

# No CMD needed — the base nginx:alpine image already defines
# the correct CMD to start Nginx in the foreground.
