from flask import Flask
import redis
import os

app = Flask(__name__)

# Connect to Redis - note we use "redis" as the hostname.
# Docker Compose creates a network where services can reach each other
# by their service name. Since our Redis service is called "redis" in
# docker-compose.yml, we can use that as the hostname here.
cache = redis.Redis(host="redis", port=6379)

@app.route("/")
def hello():
    count = cache.incr("hits")
    return f"Hello from Docker Compose! 🐳 This page has been visited {count} time(s).\n"

@app.route("/health")
def health():
    try:
        cache.ping()
        return {"status": "healthy", "redis": "connected"}
    except redis.ConnectionError:
        return {"status": "unhealthy", "redis": "disconnected"}, 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)