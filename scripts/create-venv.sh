#!/bin/bash 
  
if [ $# -lt 1 ]; then
    echo "Need project directory name for creating venv... Abort now!"
    echo "---- Usage-1: "
    echo "    source $(basename $0) <PROJECT_HOME_name> "
    echo "---- Usage-2: (assuming you install virtualenvwrapper and virutalenv)"
    echo "    mkvirtualenv ${PROJECT_HOME}"
    echo "    workon ${PROJECT_HOME}"
    exit 1
fi

PROJECT_HOME=${1:-my_venv}

PYTHON_VERSION=3
#PYTHON_VERSION=3.6

###########################################################################
#### ---------------------- DON'T CHANGE BELOW ----------------------- ####
###########################################################################
#### ---- root directory for venv setups ---- ####
WORKON_HOME=~/venv

#### ---- Detect [python3] is installed ---- ####
#### common location: /usr/bin/python3
VENV_SETUP=`cat ~/.bashrc | grep -i VIRTUALENVWRAPPER_PYTHON`
if [ ! "${VENV_SETUP}" = "" ]; then
    echo ".. virtualenvwrapper alreay has been setup!"
    exit 0
fi

#### ---- Detect [python3] is installed ---- ####
#### common location: /usr/bin/python3
PYTHON_EXE=`which python${PYTHON_VERSION}`
if [ "${PYTHON_EXE}" = "" ]; then
    echo "**** ERROR: Can't find ${PYTHON_EXE} ! .. Abort setup!"
    exit 1
fi

#### ---- Detect [virtualenv] is installed ---- ####
#### common location: /usr/local/bin/virtualenv
VIRTUALENV_EXE=`which virtualenv`
if [ "${VIRTUALENV_EXE}" = "" ]; then
    echo "**** ERROR: Can't find virtualenv executable ! .. Abort setup!"
    exit 1
fi

#### ---- Detect [virtualenvwrapper] is installed ---- ####
#### common location: /usr/local/bin/virtualenvwrapper.sh
VIRTUALENVWRAPPER_SHELL=`which virtualenvwrapper.sh`
if [ "${VIRTUALENVWRAPPER_SHELL}" = "" ]; then
    echo "**** ERROR: Can't find virtualenvwrapper.sh script! .. Abort setup!"
    exit 1
fi

#########################################################################
#### ---- Customization for multiple virtual python environment ---- ####
####      (most recommended approach and simple to switch venv)      ####
#########################################################################
#### Ref: https://virtualenvwrapper.readthedocs.io/en/latest/install.html
#### Ref: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html
#### mkvirtualenv [-a project_path] [-i package] [-r requirements_file] [virtualenv options] ENVNAME

export VIRTUALENVWRAPPER_PYTHON=${PYTHON_EXE}
export VIRTUALENVWRAPPER_VIRTUALENV=${VIRTUALENV_EXE}
# (deprecated) export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
source ${VIRTUALENVWRAPPER_SHELL}
export WORKON_HOME=${WORKON_HOME:-~/Envs}
if [ ! -d $WORKON_HOME ]; then
    mkdir -p $WORKON_HOME
fi

# To create & activate your default venv environment, say, "${PROJECT_HOME}"
echo "------"
unset PYTHONPATH
mkvirtualenv ${PROJECT_HOME}
workon ${PROJECT_HOME}

