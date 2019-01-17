FROM openkbs/jdk-mvn-py3-x11

MAINTAINER DrSnowbird "DrSnowbird@openkbs.org"

#### ---- Build Specification ----
# Metadata params
ARG BUILD_DATE=${BUILD_DATE:-}
ARG VERSION=${BUILD_DATE:-}
ARG VCS_REF=${BUILD_DATE:-}

#### ---- Product Specifications ----
ARG PRODUCT=${PRODUCT:-}
ARG PRODUCT_VERSION=${PRODUCT_VERSION:-}
ARG PRODUCT_DIR=${PRODUCT_DIR:-}
ARG PRODUCT_EXE=${PRODUCT_EXE:-}
ENV PRODUCT=${PRODUCT}
ENV PRODUCT_VERSION=${PRODUCT_VERSION}
ENV PRODUCT_DIR=${PRODUCT_DIR}
ENV PRODUCT_EXE=${PRODUCT_EXE}

# Metadata
LABEL org.label-schema.url="https://imagelayers.io" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-url="https://github.com/microscaling/imagelayers-graph.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.docker.dockerfile="/Dockerfile" \
      org.label-schema.description="This utility provides a docker template files for building Docker." \
      org.label-schema.schema-version="1.0"
      
RUN echo PRODUCT=${PRODUCT} && echo HOME=$HOME && \
    sudo apt-get install dbus-x11 && \
    sudo apt-get install -y firefox

#### --- Copy Entrypoint script in the container ---- ####
COPY ./docker-entrypoint.sh /

#### ------------------------
#### ---- user: Non-Root ----
#### ------------------------

ENV USER=${USER:-developer}
ENV USER_NAME=${USER}

ENV HOME=/home/${USER}

RUN groupadd -f --gid ${GROUP_ID} ${USER} && \
    #useradd ${USER} -m -d ${HOME} -s /bin/bash -u ${USER_ID} -g ${GROUP_ID} && \
    useradd ${USER} -m -d ${HOME} -s /bin/bash -u ${USER_ID} -g ${USER} && \
    ## -- Ubuntu -- \
    usermod -aG sudo ${USER} && \
    ## -- Centos -- \
    #usermod -aG wheel ${USER} && \
    echo "${USER} ALL=NOPASSWD:ALL" | tee -a /etc/sudoers && \
    export uid=${USER_ID} gid=${GROUP_ID} && \
    chown ${USER}:${USER} -R ${HOME}
    
RUN mkdir -p ${HOME}/workspace && \
    chown ${USER}:${USER} -R ${HOME}/workspace

WORKDIR ${HOME}

USER ${USER}

#### --- Enterpoint for container ---- ####
USER ${USER_NAME}
WORKDIR ${HOME}

ENTRYPOINT ["/docker-entrypoint.sh"]

#### (Test only)
CMD ["/usr/bin/firefox"]
#CMD ["startx /usr/bin/firefox"]
#CMD ["/bin/bash"]

