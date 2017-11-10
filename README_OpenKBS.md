# Docker Project Template

## Purpose
To provide the common files for building, running a docker project

## Concepts:
### Simple command-based Docker environments:
- Docker environment should be very simple as just one click (or one command) to start a Docker-based applications without fudging and mistakes in launch containers.
- Provide the simplest (ready-to-use) way for running Docker-based command-based envionrment for supporing daily development needs ranging from base docker images (e.g. JDK, Python, ...) up to advanced applications/servers (e.g., scala-ide-docker, Netbean-docker, Eclipse-docker, and many other big data analytics, machine learning, and semantic knowlege graph applications/servers).

### Only needs two scripts: "./run.sh" and "./build.sh"
- "./run.sh" to instantly stand up your Docker-based application development environment (note that, for Product usage, please enhance all aspects of security -- we are not responsible for security ignornace for your deployments since it is your responsibility)

### Pure Container-based Developer Desktop paradigm
- With our above "simple-minded simple-use", we provide many commonly used "pure docker-based IDEs, Applications, Servers" for software development daily needs.

## Where to start:
- This project template folder assumes you like to adop and use simple command-based Docker lifecycle paradigm as publicly available in:
1. OpenKBS GIT HUB [https://hub.docker.com/r/openkbs/] - for pulling the ready to use public Docker Images
2. OpenKBS Docker HUB [https://github.com/DrSnowbird/] - for advanced users like to build and customize to your own flavor using our open source environments.

## Pre-requisite tool to get you start from a new (freshly installed) Host OS envionrment
- Use those scripts under ./bin has several useful bash scripts to jump start what you need.
1. dockerCE-install.sh: Install docker CE with latest version available.

# To Start using OpenKBS Containers

## Preparation
- Create a common folder as the root of any OpenKBS's container source code you pull down, e.g.
```
mkdir $HOME/my-github/
cd $HOME/my-github/
```
## Pull
- Just pull from OpenKBS GIT HUB [https://hub.docker.com/r/openkbs/] to have local source code for specific OpenKBS GIT.
You should already in the $HOME/my-github/ already, if not go do the above steps again.
- Now, pull any OpenKBS GitHub
```
git pull https://github.com/DrSnowbird/<container_name>.git
```
e.g.,
```
cd $HOME/my-github/
git pull https://github.com/DrSnowbird/scala-ide-docker.git
```

## Run
- To run the simple example build image; it will pop up X11 to display Firefox docker-based browser.
Change directory into the new folder just created by the pulling of above "git pull".

```
cd scala-ide-docker
./run.sh
```
- It will pop up an GUI for user interaction use like Eclipse, or Netbeans.

## Build (You like to build your local image)
```
./build.sh
```
- (advanced use) You can modify the script to have own image tag by changing "openkbs" to "my" (or whatever name you choose) and run ./build.sh

## Additional tools for managing your Containers
1. portainer_resume.sh: Launch portainer to manage all you Docker-based containers (some
2. container-launcher.sh: Launch any
