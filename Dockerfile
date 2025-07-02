FROM mambaorg/micromamba AS runtime_micromamba
USER root

# Set environment variables early
ENV DEBIAN_FRONTEND=noninteractive \
    MAMBA_DOCKERFILE_ACTIVATE=1 \
    PATH=/opt/conda/envs/mcp_pymdu/bin:$PATH \
    CONDA_DEFAULT_ENV=/opt/conda/envs/mcp_pymdu

# Install system dependencies in a single layer
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

# Create the environment:
COPY ./environment.yml .
RUN micromamba env create -f environment.yml -p /opt/conda/envs/mcp_pymdu

SHELL ["micromamba", "run", "-n", "mcp_pymdu", "/bin/bash", "-c"]

WORKDIR /app

# Copy application code last
COPY . .

# install poetry
ARG PYPI_MIRROR
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    if [ -n "$PYPI_MIRROR" ]; then \
        pip config set global.index-url $PYPI_MIRROR; \
    fi && \
    python -m pip install --upgrade pip poetry && \
    poetry config cache-dir /root/.cache/pypoetry && \
    poetry install --no-interaction --no-ansi



CMD ["/opt/conda/envs/mcp_pymdu/bin/fastmcp", "run", "/app/mcp_pymdu/server.py", "--transport", "stdio"]
#ENTRYPOINT ["micromamba", "run", "-n", "mcp_pymdu", "/bin/bash", "-c", "python -m mcp_pymdu.server"]