#!/bin/bash

# Define project directories and files
PROJECT_DIR="project_root"
BACKEND_DIR="${PROJECT_DIR}/backend"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
TILES_DIR="${PROJECT_DIR}/tiles"
PROMETHEUS_CONFIG="${PROJECT_DIR}/prometheus.yml"
DOCKER_COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
DEVCONTAINER_DIR="${PROJECT_DIR}/.devcontainer"
DEVCONTAINER_FILE="${DEVCONTAINER_DIR}/devcontainer.json"

# Create directory structure
mkdir -p "$BACKEND_DIR"
mkdir -p "$FRONTEND_DIR"
mkdir -p "$TILES_DIR"
mkdir -p "$DEVCONTAINER_DIR"

# Create Dockerfile for Django
cat <<EOL > "${BACKEND_DIR}/Dockerfile"
# Use the official Python image from the Docker Hub
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOL

# Create Dockerfile for React
cat <<EOL > "${FRONTEND_DIR}/Dockerfile"
# Use the official Node.js image from the Docker Hub
FROM node:latest

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the application code into the container
COPY . /app/

# Build the React application
RUN npm run build

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the React application
CMD ["npm", "start"]
EOL

# Create Docker Compose file
cat <<EOL > "$DOCKER_COMPOSE_FILE"
version: '3.8'

services:
  django:
    image: python:3.11
    container_name: django
    working_dir: /app
    command: bash -c "pip install -r requirements.txt && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - kafka
    environment:
      - POSTGRES_DB=\${POSTGRES_DB}
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - KAFKA_BROKER=kafka:9092

  react:
    image: node:latest
    container_name: react
    command: npm start
    working_dir: /app/frontend
    volumes:
      - ./frontend:/app/frontend
    ports:
      - "3000:3000"

  postgres:
    image: postgis/postgis:latest
    container_name: postgres
    environment:
      POSTGRES_DB: \${POSTGRES_DB}
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:latest
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  zookeeper:
    image: wurstmeister/zookeeper:latest
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: wurstmeister/kafka:latest
    container_name: kafka
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"

  osm-tile-server:
    image: overv/openstreetmap-tile-server:latest
    container_name: osm-tile-server
    depends_on:
      - postgres
    environment:
      UPDATES: "true"
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASS: \${POSTGRES_PASSWORD}
      POSTGRES_DB: \${POSTGRES_DB}
    ports:
      - "80:80"
    volumes:
      - tiles_data:/var/lib/posttiles

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    depends_on:
      - prometheus
    ports:
      - "3001:3000"

  dbeaver:
    image: dbeaver/cloudbeaver:latest
    container_name: dbeaver
    ports:
      - "8080:8080"
    environment:
      CB_ADMIN_NAME: admin
      CB_ADMIN_PASSWORD: admin
    volumes:
      - dbeaver_data:/opt/cloudbeaver/workspace

volumes:
  postgres_data:
  redis_data:
  tiles_data:
  dbeaver_data:
EOL

# Create devcontainer.json file
cat <<EOL > "$DEVCONTAINER_FILE"
{
  "name": "Project Development Container",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "django",
  "workspaceFolder": "/app",
  "extensions": [
    "ms-python.python",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "redhat.vscode-yaml"
  ],
  "settings": {
    "python.pythonPath": "/usr/local/bin/python",
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
  },
  "postCreateCommand": "pip install -r requirements.txt",
  "remoteUser": "vscode",
  "mounts": [
    "source=${localWorkspaceFolder}/backend,target=/app,type=bind",
    "source=${localWorkspaceFolder}/frontend,target=/app/frontend,type=bind"
  ]
}
EOL

# Create Prometheus configuration file
cat <<EOL > "$PROMETHEUS_CONFIG"
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka:9092']

  - job_name: 'zookeeper'
    static_configs:
      - targets: ['zookeeper:2181']

  - job_name: 'osm-tile-server'
    static_configs:
      - targets: ['osm-tile-server:80']
EOL

# Output success message
echo "Project structure and files have been created successfully."
