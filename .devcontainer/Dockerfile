# Use the base image for your dev container
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install Docker CLI, Docker Compose, curl, and Docker Debug
RUN apt-get update && \
    apt-get install -y \
    curl \
    docker-compose \
    gnupg \
    lsb-release && \
    # Install Docker CLI
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    # Install Docker Debug CLI
    curl -LO https://download.docker.com/linux/static/stable/x86_64/docker-20.10.8.tgz && \
    tar xzvf docker-20.10.8.tgz && \
    mv docker/* /usr/local/bin/ && \
    chmod +x /usr/local/bin/docker* && \
    # Clean up
    rm -rf docker-20.10.8.tgz docker && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any other dependencies you need

# Default command to keep the container running
CMD ["sleep", "infinity"]