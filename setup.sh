#!/bin/bash 

set -e
env

#### ---------------------
#### --- APP: LOCATION ---
#### ---------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [[ "$DIR" =~ "app$" ]]; then
    APP_HOME=${APP_HOME:-${DIR}}
else
     # - find possilbe app directory: 
    #APP_HOME=`realpath $(find ./ -name app)`
    if [ -d $DIR/app ]; then
        APP_HOME=${DIR}/app
    fi
fi

#### ---------------------------
#### --- APP: DATA Directory ---
#### ---------------------------
APP_DATA_DIR=${APP_DATA_DIR:-$HOME/data}

# -------------------------------
# ----------- Usage -------------
# -------------------------------
# To test on host machine:
# Run the Application:
#   ./setup.sh
# -------------------------------
# -- example --
#mvn clean
#mvn package -Dmaven.test.skip=true
#java -jar target/swagger-spring-1.0.0.jar --server.port=8889

#### ------------------------------------
#### ---- APP: Programming Profile:  ----
#### ------------------------------------
APP_TOOLS=${APP_TOOLS:-"java javac mvn unzip"}
APP_TOOLS=${APP_TOOLS:-"java javac unzip"}

#### ---- Programming Modoel: ant, maven, javac, other  ----
#APP_BUILD_MODEL="ant"
#APP_BUILD_MODEL="maven"

APP_CLEAN_DIR=${APP_CLEAN_DIR:-${APP_HOME}}
#APP_CLEAN_CMD="ant clean"
#APP_CLEAN_CMD="mvn clean"

APP_BUILD_DIR=${APP_BUILD_DIR:-${APP_HOME}}
#APP_BUILD_CMD="ant dist"
#APP_BUILD_CMD="mvn package -Dmaven.test.skip=true"

#APP_RUN_DIR=$APP_HOME/dist
#APP_RUN_CMD="java -jar some-app.jar"
#APP_RUN_CMD="java -jar target/swagger-spring-1.0.0.jar --server.port=8889"

## -- Additional APP's RUN arguments: --
#APP_RUN_ARGS=

BUILD_MODEL_SUPPORTED="ant maven javac"
function detectBuildModel() {
    ## -- Currently only support ant, maven, javac as build models --
    if [ -s "$APP_BUILD_DIR/build.xml" ]; then
         APP_BUILD_MODEL="ant"
    elif [ -s "$APP_BUILD_DIR/pom.xml" ]; then
         APP_BUILD_MODEL="maven"
    #elif [ -s "$APP_BUILD_DIR/build.gradle" ]; then
    #     APP_BUILD_MODEL="gradle"
    else
         APP_BUILD_MODEL="javac"
    fi 
}
if [  "$APP_BUILD_MODEL" = "" ]; then
    detectBuildModel 
fi

modelMatched=0
function verifyBuildModelSupported() {
    for model in $BUILD_MODEL_SUPPORTED; do
        if [ $modelMatched -lt 1 ]; then
             if [ "$APP_BUILD_MODEL" = "$model" ]; then
                 modelMatched=1
             fi
        fi
    done
    if [ $modelMatched -eq 0 ]; then
         echo "*** ERROR: verifyBuildModelSupported():NOT_SUPPORTED_BUILD_MODEL: -- Abort now!"
         exit 1
    else
         echo "--- INFO: verifyBuildModelSupported():BUILD_MODEL_SUPPRTED: $APP_BUILD_MODEL"
    fi
}
verifyBuildModelSupported

function verifyDirectory() {
    if [ "$1" = "" ] || [ ! -d "$1" ]; then
        echo "*** ERROR ***: NOT_EXISTING: App's mandatory directory: $1: Can't continue! Abort!"
        exit 1
    fi
}

function verifyFile() {
    if [ "$1" != "" ] && [ ! -s "$1" ]; then
        echo "*** ERROR ***: NOT_FOUND: App's mandatory file: $1: Can't continue! Abort!"
        exit 1
    fi
}

function verifyCommand() {
    for tool in $* ; do
        if [ ! `which $tool` ]; then
            echo "*** ERROR ***: NOT_FOUND: App's mandatory tool: $tool: Can't continue! Abort!"
            exit 1
        fi
    done
}

function runCommands() {
    if [ "$1" != "" ] && [ -d "$1" ]; then
        cd $1
        shift
    fi
    if [ "$1" != "" ]; then
        /bin/bash -c "$*"
    fi
}

verifyCommand ${APP_TOOLS}

# -------------------------------------------------------------------------------------

#### ---------------------------------------
#### ---- APP: BUILD (automation setup) ----
#### ---------------------------------------
function setupAppBuildInfo() {
    case $1 in
      ant*)
        verifyCommand ant
        APP_CLEAN_CMD=${APP_CLEAN_CMD:-"ant clean"}
        APP_BUILD_CMD=${APP_BUILD_CMD:-"ant dist"}
        ;;
      maven*)
        verifyCommand mvn
        APP_CLEAN_CMD=${APP_CLEAN_CMD:-"mvn clean"}
        APP_BUILD_CMD=${APP_BUILD_CMD:-"mvn package"}
        # APP_BUILD_CMD=${APP_BUILD_CMD:-"mvn package -Dmaven.test.skip=true"}
        ;;
      java*)
        verifyCommand javac
        APP_CLEAN_CMD=${APP_CLEAN_CMD:-"rm -f *.class"}
        APP_BUILD_CMD=${APP_BUILD_CMD:-"javac *.java"}
        ;;
      *)
        echo "*** setup.sh: setupBuildInfo():ERROR: -- Unsupported Programming model for template! Abort!"
        exit 1
        ;;
    esac
}
if [  "$APP_BUILD_CMD" = "" ]; then
    setupAppBuildInfo ${APP_BUILD_MODEL}
fi

echo "(final)>>> APP_BUILD_DIR=$APP_BUILD_DIR"

#### ---- Verify directory ----
verifyDirectory $APP_HOME
verifyDirectory $APP_BUILD_DIR

#### ---- BUILD Application ----
runCommands "${APP_BUILD_DIR}" "${APP_CLEAN_CMD}" 
runCommands "${APP_BUILD_DIR}" "${APP_BUILD_CMD}"

#### ---------------------------------------
#### ---- APP: RUN (automation setup) ----
#### ---------------------------------------
#APP_RUN_CMD="java -jar some-app.jar"
#APP_RUN_CMD="java -jar target/swagger-spring-1.0.0.jar --server.port=8889"
function setupAppRunInfo() {
    case $1 in
      ant*)
        APP_RUN_DIR=${APP_RUN_DIR:-$APP_HOME/dist}
        ;;
      maven*)
        APP_RUN_DIR=${APP_RUN_DIR:-$APP_HOME/target}
        ;;
      java*)
        APP_RUN_DIR=${APP_RUN_DIR:-$APP_HOME}
        ;;
      *)
        echo "*** setup.sh: setupAppRunInfo():ERROR: -- Unsupported Programming model for template! Abort!"
        exit 1
        ;;
    esac
}
if [  "$APP_RUN_DIR" = "" ]; then
    setupAppRunInfo ${APP_BUILD_MODEL}
fi
echo "(final)>>> APP_RUN_DIR=$APP_RUN_DIR"

verifyDirectory $APP_RUN_DIR

#### -------------------------------------------------
#### --- APP: Detect Jar, Main_Class for running: ----
#### -------------------------------------------------
function setupAppRunMainClassInfo() {
    # e.g.APP_RUN_CMD=${APP_RUN_CMD:-"java -jar ${APP_HOME}/some-app.jar"}
        ## -- Need to auto-detect APP_RUN_JAR and APP_RUN_MAIN_CLASS: --
    if [ "$APP_RUN_JAR" = "" ]; then
        FOUND_JAR=`ls ${APP_RUN_DIR}/*.jar | awk '{print $1}' `
        if [ "$FOUND_JAR" != "" ]; then
            APP_RUN_JAR=${APP_RUN_JAR:-${FOUND_JAR}}
        else
            ## -- to create failure for later checking existence since no Jar found - need to fail out --
            APP_RUN_JAR=${APP_RUN_JAR:-non-existing.jar}
            echo "*** setup.sh:FAIL: -- Can't find definition of APP_RUN_JAR in Environmant variables! Abort!"
            exit 1
        fi
    fi
    # -- verify APP_RUN_JAR: defined && existing in filesystem
    if [ "${APP_RUN_JAR}" = "" ] || [ ! -s ${APP_RUN_JAR} ]; then
        echo "*** ERROR:FAIL: -- APP_RUN_JAR variable is not defined or cant' find the Jar file $APP_RUN_JAR"
        exit 1
    fi
    # -- auto-detect Jar's manifest's Main_Class
    APP_RUN_MAIN_CLASS_DETECT="`unzip -q -c ${APP_RUN_JAR} META-INF/MANIFEST.MF|grep Main-Class | awk '{print $2}' |tr -d '\r'`"
    APP_RUN_MAIN_CLASS=${APP_RUN_MAIN_CLASS:-$APP_RUN_MAIN_CLASS_DETECT}
    #### ---- For Hello: it is "com.mycompany.app.Hello" 
    #### ---- Either provide APP_RUN_CMD (the simple and general
    APP_RUN_CMD=${APP_RUN_CMD:-"java -cp ${APP_RUN_JAR} ${APP_RUN_MAIN_CLASS} "}
    # (in .env) APP_RUN_CMD="java -cp target/my-app-1.0-SNAPSHOT.jar com.mycompany.app.Hello"
}
if [ "$APP_BUILD_MODEL" != "javac" ]; then
    if [  "$APP_RUN_CMD" = "" ] || [ "$APP_RUN_JAR" = "" ]; then
        setupAppRunMainClassInfo
    fi
else
    # javac simple project
    tmpJavaClass=`ls  $APP_HOME/*.class | awk '{print $1}'`
    findJavaClass=${tmpJavaClass%.class}
    javaClass=$(basename $findJavaClass)
    APP_RUN_CMD=${APP_RUN_CMD:-"java ${javaClass}"}
fi

#### ---- Application ----
cd ${APP_RUN_DIR} 
ls -al 

verifyFile $APP_RUN_JAR

echo "(final)>>> APP_RUN_DIR=$APP_RUN_DIR"
echo "(final)>>> APP_RUN_CMD=$APP_RUN_CMD"
echo "(final)>>> APP_RUN_JAR=$APP_RUN_JAR"
echo "(final)>>> APP_RUN_ARGS=$APP_RUN_ARGS"

#### ---- RUN Application ----
# e.g.:  cd ${APP_HOME}/dist && java -jar some-app.jar
#
if [ "${APP_HOME}" != "" ] && [ "${APP_RUN_CMD}" != "" ]; then
    runCommands "${APP_HOME}" "${APP_RUN_CMD}" ${APP_RUN_ARGS}
else
    echo "*** ERROR: either ${APP_RUN_DIR} or ${APP_RUN_CMD} is empty: Can' continue/run Java application! Abort!"
    exit 1
fi

