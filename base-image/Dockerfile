FROM ubuntu:18.04
# Master build file for pangeo images!

# Run this section as root
# ========================

# Environment variables
ENV CONDA_VERSION=4.8.2
ENV NB_USER=jovyan
ENV NB_UID=1000
ENV SHELL=/bin/bash
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV CONDA_DIR=/srv/conda
ENV NB_PYTHON_PREFIX=${CONDA_DIR}/envs/pangeo
ENV HOME=/home/${NB_USER}

# Copy auxiliary files
COPY start dask_config.yml conda.sh condarc /tmp/

WORKDIR /tmp

# Apt Packages
RUN apt-get update --fix-missing \
    && apt-get install wget -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create group + user, and set proper permissions on home & conda directories
RUN groupadd --gid ${NB_UID} ${NB_USER} \
    && useradd --comment "Default user" --create-home --gid ${NB_UID} \
        --no-log-init --shell /bin/bash --uid ${NB_UID} ${NB_USER}

# Install standalone conda
RUN wget --quiet -O conda -q https://repo.anaconda.com/pkgs/misc/conda-execs/conda-4.7.12-linux-64.exe \
    && chmod +x conda \
    && mkdir ${CONDA_DIR} \
    && cat condarc | ./conda config --stdin  \
    && ./conda create -n pangeo conda=${CONDA_VERSION} \
    && mv condarc ${CONDA_DIR}/envs/pangeo/.condarc \
    && ./conda clean -afy \
    && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete

# Move things around filesystem
RUN chmod +x start \
    && cp start /srv/start \
    && mkdir /etc/dask \
    && cp dask_config.yml /etc/dask/dask.yml \
    && cat conda.sh > /etc/profile.d/conda.sh \
    && chown -R ${NB_USER}:${NB_USER} /srv \
    && rm -r /tmp


# Only run these if used as a base image
# ----------------------
ONBUILD USER root
ONBUILD COPY . ${HOME}
ONBUILD RUN [ -d binder ] && cd binder \
        ; if test -f "apt.txt" ; then \
        apt-get update --fix-missing \
        && xargs -a apt.txt apt-get install -y \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* \
        ; fi
ONBUILD RUN chown -R ${NB_USER}:${NB_USER} ${HOME}
# ----------------------


# Run this section as unprivileged jovyan
# ==========
USER ${NB_USER}
WORKDIR $HOME

# Only run if used as a base image
# ----------------------
ONBUILD USER ${NB_USER}

# Create "pangeo" environment from environment.yml
# Get pangeodask version from environment.yml
# NOTE: not sure if we need to pin pangeo-dask and pangeo-notebook images
ONBUILD RUN [ -d binder ] && cd binder \
        ; if test -f "environment.yml" ; then \
        export PATH=${CONDA_DIR}/bin:$PATH \
        && conda env create -f environment.yml \
        && echo "conda activate pangeo" >> ${CONDA_DIR}/etc/profile.d/conda.sh \
        && conda clean -afy \
        && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
        && find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete \
        && find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete \
#        && find ${NB_PYTHON_PREFIX}/lib/python*/site-packages/bokeh/server/static -follow -type f -name '*.js' ! -name '*.min.js' -delete \
        ; fi

# Run postBuild script within "pangeo" environment
ONBUILD RUN [ -d binder ] && cd binder \
        ; if test -f "postBuild" ; then \
        export PATH=${NB_PYTHON_PREFIX}/bin:$PATH \
        && chmod +x postBuild \
        && ./postBuild \
        && rm -rf ${HOME}/.cache ${HOME}/.npm ${HOME}/.yarn \
        && rm -rf ${NB_PYTHON_PREFIX}/share/jupyter/lab/staging \
        && find ${NB_PYTHON_PREFIX} -follow -type f -name '*.js.map' -delete \
        ; fi

# Overwrite start entrypoint script if present
ONBUILD RUN [ -d binder ] && cd binder \
        ; if test -f "start" ; then \
        chmod +x start \
        && cp start /srv/start \
        ; fi
# ----------------------

EXPOSE 8888

ENTRYPOINT ["/srv/start"]
#CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
