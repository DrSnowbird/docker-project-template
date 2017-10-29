# Docker Project Template
## Purpose
To provide the common files for building, running a docker project
## Usage
1. Copy all the folder's files to your destination, i.e., your new project folder.
2. Globally replace "docker-project-template" for all the files with your new Docker project repo name, e.g., scala-ide-docker.
3. Modify two or three files below depending upon your use case:
- Dockerfile
- docker-compose.yaml
- docker.env (if you need to modify docker environments input file)
## Build
- This project provides a simple Dockerfile for the purpose of illustration only. You need to extend/modify the Docker to 
support whatever you want to do.
```
./build.sh
```
## Run
- To run the simple example build image; it will pop up X11 to display Firefox docker-based browser. 
```
./run.sh
```
