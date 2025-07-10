# # syntax=docker/dockerfile:1

# # Comments are provided throughout this file to help you get started.
# # If you need more help, visit the Dockerfile reference guide at
# # https://docs.docker.com/go/dockerfile-reference/

# # Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

# ARG PYTHON_VERSION=3.13.3
# FROM python:${PYTHON_VERSION}-slim as base

# # Prevents Python from writing pyc files.
# ENV PYTHONDONTWRITEBYTECODE=1

# # Keeps Python from buffering stdout and stderr to avoid situations where
# # the application crashes without emitting any logs due to buffering.
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# # Create a non-privileged user that the app will run under.
# # See https://docs.docker.com/go/dockerfile-user-best-practices/
# ARG UID=10001
# RUN adduser \
#     --disabled-password \
#     --gecos "" \
#     --home "/nonexistent" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     appuser

# # Download dependencies as a separate step to take advantage of Docker's caching.
# # Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# # Leverage a bind mount to requirements.txt to avoid having to copy them into
# # into this layer.
# RUN --mount=type=cache,target=/root/.cache/pip \
#     --mount=type=bind,source=requirements.txt,target=requirements.txt \
#     python -m pip install -r requirements.txt

# # Switch to the non-privileged user to run the application.
# USER appuser

# # Copy the source code into the container.
# COPY . .

# # Expose the port that the application listens on.
# EXPOSE 5000

# # Run the application.
# CMD python app.py



FROM mongo:6.0

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install pymongo && \
    rm -rf /var/lib/apt/lists/*

# Copy initialization scripts and data
COPY init-mongo.py /docker-entrypoint-initdb.d/
COPY sample-data.json /docker-entrypoint-initdb.d/

# Make the Python script executable
RUN chmod +x /docker-entrypoint-initdb.d/init-mongo.py

# Create a custom entrypoint script
RUN echo '#!/bin/bash\n\
# Start MongoDB in background\n\
mongod --fork --logpath /var/log/mongodb.log --dbpath /data/db\n\
\n\
# Wait for MongoDB to start\n\
sleep 10\n\
\n\
# Run Python initialization script\n\
python3 /docker-entrypoint-initdb.d/init-mongo.py\n\
\n\
# Stop the background MongoDB\n\
mongod --shutdown --dbpath /data/db\n\
\n\
# Start MongoDB normally\n\
exec mongod --dbpath /data/db\n\
' > /usr/local/bin/custom-entrypoint.sh && chmod +x /usr/local/bin/custom-entrypoint.sh

# Expose MongoDB port
EXPOSE 27017

# Use custom entrypoint
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]