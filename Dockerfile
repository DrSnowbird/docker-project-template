FROM openkbs/jdk-mvn-py3-x11

MAINTAINER DrSnowbird "DrSnowbird@openkbs.org"
RUN echo $HOME
CMD ["/usr/bin/firefox"]
