
VERSION=1.0.0
PROJECT := docker-project-template
DOCKER_REPO := openkbs

SHA := $(shell git describe --match=NeVeRmAtCh --always --abbrev=40 --dirty=*)

build:
	docker build --build-arg CIRCLE_SHA1="$(SHA)" --build-arg edition=ce --build-arg version=${VERSION} -t openkbs/$${docker-project-template}:${VERSION} .

upload: build
	docker push ${DOCKER_REPO}/$${docker-project-template}:${VERSION}

up:
	docker-compose up -d

down:
	docker-compose down

rmi:
	docker rmi $$(docker images -f dangling=true -q)

exec:
	docker-compose exec $${docker-project-template} /bin/bash
