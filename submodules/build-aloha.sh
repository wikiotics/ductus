#!/bin/bash

set -e

# build aloha from the sources in the git submodule.
# to run this script you need node.js installed.
# (apt-get install nodejs for debian/ubuntu, for other systems http://nodejs.org)

# for development, it's easier to NOT build aloha, and just let require.js do it's job live
# it means slowler loading times, but much easier development, as there is no need to recompile after every change :)
# to switch to "dev mode", call the script with "-d" option.
while getopts ":d" opt; do
  case $opt in
    d)
      DEV_MODE=1
      ;;
    \?)
      echo "Usage: $0 [-d] where -d runs the build in developer mode (see docs)" >&2
      exit 1
      ;;
  esac
done

# build aloha.js
AE_BASE=../../../../submodules/Aloha-Editor
AE_SRC=$AE_BASE/src

cd ../ductus/static/modules/textwiki
# remove the build directory
rm -rf aloha
mkdir -p aloha/plugins

if [ $DEV_MODE ]; then
    # DevMode, just copy files, so writing code/testing is simplified
    echo "(not) building aloha JS for development"
    cp -R $AE_SRC/lib aloha/lib
    cp -R $AE_SRC/plugins aloha/
    # these are our own files, most likely to be amended, hardlink them so aloha finds them, and git stays happy :)
    # note that this overwrites any aloha stock files, which mimicks the production setup
    cp -flR js/aloha-plugins/* aloha/plugins
else
    # copy our own plugins, and build aloha into a single file
    echo "building aloha JS for production"
    cp -R js/aloha-plugins/* aloha/plugins
    node $AE_BASE/build/r.js -o ./build-aloha-for-ductus.js
fi

# compile aloha.css
# this will probably trigger some warnings about CSS imports missing (aloha-sidebar.css and repository-browser.css), they're on purpose,
# to prevent problems when deploying code with Django's manage.py collectstatic that would look for files that do not exist.
if [ $DEV_MODE ]; then
    echo "copying css files"
    cp -R $AE_SRC/css aloha
    cp -R $AE_SRC/img aloha
else
    mkdir -p aloha/css
    cp aloha-css-for-ductus.css_template aloha/css/aloha-css-for-ductus.css
    node $AE_BASE/build/r.js -o cssIn=aloha/css/aloha-css-for-ductus.css out=aloha/css/aloha.css optimizeCss=standard
    # remove original css files after compiling them into aloha.css so they don't trigger errors in the django collectstatic stage
    echo "removing CSS source files"
    rm aloha/css/aloha-*
    echo "removing any @import statements left in aloha.css"
    sed -i 's/@import[^;]*;//g'  aloha/css/aloha.css
fi
