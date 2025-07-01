
FROM mambaorg/micromamba AS runtime_micromamba
USER root
# install apt dependencies
RUN --mount=type=cache,target=/var/cache/apt \
   export DEBIAN_FRONTEND=noninteractive && \
   apt-get update && \
   apt-get upgrade -y && \
   apt-get install -y --no-install-recommends --no-install-suggests build-essential \
    vim zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev \
    libsqlite3-dev wget libbz2-dev libpq-dev libssl-dev libffi-dev libxml2-dev \
    libxslt1-dev zlib1g-dev apt-transport-https dirmngr gnupg ca-certificates unzip wkhtmltopdf

RUN --mount=type=cache,target=/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends git wget gcc g++ make pkg-config apt-utils procps \
    && apt-get install -y  software-properties-common \
    && apt-get install -y  --no-install-recommends openjdk-17-jre-headless \
    && apt-get install -y --no-install-recommends libxmlsec1-dev \
    && apt-get install -y --no-install-recommends libgl1-mesa-dri gosu iputils-ping xvfb

ARG MAMBA_DOCKERFILE_ACTIVATE=1
# Create the environment:
COPY ./environment.yml .
RUN micromamba env create -f environment.yml -p /opt/conda/envs/umep_pymdu

# Définir l'environnement par défaut
ENV PATH=/opt/conda/envs/umep_pymdu/bin:$PATH
ENV CONDA_DEFAULT_ENV=/opt/conda/envs/umep_pymdu

SHELL ["micromamba", "run", "-n", "mcp_pymdu", "/bin/bash", "-c"]
WORKDIR /app

COPY . .
# install poetry
ARG PYPI_MIRROR
RUN if [ -n "$PYPI_MIRROR" ]; then pip config set global.index-url $PYPI_MIRROR; fi
RUN --mount=type=cache,target=/app/.cache python -m pip install --upgrade pip
RUN --mount=type=cache,target=/app/.cache poetry install --no-interaction --no-ansi -vvv


#CMD ["python", "server.py"]
CMD ["micromamba", "run", "-n", "mcp_pymdu", "/bin/bash", "-c", "python server.py"]
