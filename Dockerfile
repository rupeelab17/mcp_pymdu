# This Dockerfile section sets up a Python application environment using micromamba and Poetry.
# Here's what each part does:

# 1. Use the micromamba base image for efficient conda environment management.
FROM mambaorg/micromamba AS runtime_micromamba

# 2. Switch to the root user to install system packages.
USER root

# 3. Set environment variables early for non-interactive apt installs and to activate the conda environment by default.
ENV DEBIAN_FRONTEND=noninteractive \
    MAMBA_DOCKERFILE_ACTIVATE=1 \
    PATH=/opt/conda/envs/mcp_pymdu/bin:$PATH \
    CONDA_DEFAULT_ENV=/opt/conda/envs/mcp_pymdu

# 4. Install all required system dependencies in a single layer for efficiency.
#    Uses build caches for apt to speed up rebuilds.
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        build-essential \
        vim \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        libbz2-dev \
        libpq-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        apt-transport-https \
        dirmngr \
        gnupg \
        ca-certificates \
        unzip \
        wkhtmltopdf \
        git \
        gcc \
        g++ \
        make \
        pkg-config \
        apt-utils \
        procps \
        software-properties-common \
        openjdk-17-jre-headless \
        libxmlsec1-dev \
        libgl1-mesa-dri \
        gosu \
        iputils-ping \
        xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 5. Copy the conda environment specification and create the environment.
COPY ./environment.yml .
RUN micromamba env create -f environment.yml -p /opt/conda/envs/mcp_pymdu

# 6. Set the default shell to run commands inside the conda environment.
SHELL ["micromamba", "run", "-n", "mcp_pymdu", "/bin/bash", "-c"]

# 7. Set the working directory for the application.
WORKDIR /app

# 8. Copy the application code into the image.
COPY . .

# 9. Install Poetry and project dependencies.
#    Optionally uses a custom PyPI mirror if provided.
ARG PYPI_MIRROR
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    if [ -n "$PYPI_MIRROR" ]; then \
        pip config set global.index-url $PYPI_MIRROR; \
    fi && \
    python -m pip install --upgrade pip poetry && \
    poetry config cache-dir /root/.cache/pypoetry && \
    poetry install --no-interaction --no-ansi

# 10. Set the default command to run the application using fastmcp.
CMD ["/opt/conda/envs/mcp_pymdu/bin/fastmcp", "run", "/app/mcp_pymdu/server.py", "--transport", "stdio"]
# Alternative entrypoint (commented out): run the server module directly with Python.
#ENTRYPOINT ["micromamba", "run", "-n", "mcp_pymdu", "/bin/bash", "-c", "python -m mcp_pymdu.server"]