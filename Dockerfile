FROM openkbs/jdk11-mvn-py3-x11

MAINTAINER DrSnowbird "DrSnowbird@openkbs.org"

ENV DISPLAY=${DISPLAY:-":0.0"}

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
LABEL org.label-schema.url="https://openkbs.org/" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-url="https://github.com/DrSnowbird/docker-project-template.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.docker.dockerfile="/Dockerfile" \
      org.label-schema.description="This utility provides a docker template files for building Docker." \
      org.label-schema.url="https://openkbs.org/" \
      org.label-schema.schema-version="1.0"
      
#### --- Copy Entrypoint script in the container ---- ####
COPY --chown=$USER ./docker-entrypoint.sh /

RUN echo "Set disable_coredump false" | sudo tee -a /etc/sudo.conf

# ref: https://linuxize.com/post/how-to-install-google-chrome-web-browser-on-debian-10/
#### ---------------------------------------------------------------
#### ----  Install Google Chrome Web Browser on Debian 10 Linux ----
#### ---------------------------------------------------------------
ARG GOOGLE_DEB=${GOOGLE_DEB:-google-chrome-stable_current_amd64.deb}
RUN sudo apt-get -y update && sudo apt-get install -y dbus-x11 && \
    sudo wget -qc https://dl.google.com/linux/direct/${GOOGLE_DEB} && \
    sudo apt-get install -y ./${GOOGLE_DEB} && \
    sudo rm -f ./${GOOGLE_DEB}
    
#ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
#RUN sudo chmod -R 0777 /host/run/dbus/system_bus_socket

RUN sudo chmod -R 0777 /host/run/dbus/system_bus_socket

#### ------------------------
#### ---- python3: venv  ----
#### ------------------------
RUN mkdir ${HOME}/bin
COPY --chown=$USER:$USER ./bin/create-venv.sh ${HOME}/bin/
COPY --chown=$USER:$USER ./bin/setup_venv_bash_profile.sh ${HOME}/bin/

RUN sudo chown -R $USER:$USER ${HOME} && sudo chmod +x ${HOME}/bin/*.sh 
RUN ${HOME}/bin/create-venv.sh myvenv
RUN ${HOME}/bin/setup_venv_bash_profile.sh

RUN ls -al $HOME/bin

#### ------------------------
#### ---- user: Non-Root ----
#### ------------------------

#### --- Enterpoint for container ---- ####
USER ${USER}
WORKDIR ${HOME}

ENTRYPOINT ["/docker-entrypoint.sh"]
#CMD ["/usr/bin/firefox"]
#CMD ["/usr/bin/google-chrome","--no-sandbox","--disable-gpu","--disable-extensions"]
CMD ["/usr/bin/google-chrome","--no-sandbox","--disable-gpu"]

