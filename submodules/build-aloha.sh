#!/bin/bash

# build aloha from the sources in the git submodule.
# to run this script you need node.js installed.
# (apt-get install nodejs for debian/ubuntu, for other systems http://nodejs.org)

# build aloha.js
cd ../ductus/static/modules/textwiki
# remove the build directory
rm -rf aloha
mkdir -p aloha/plugins
# copy our own plugins
cp -R js/aloha-plugins/* aloha/plugins
node ../../../../submodules/Aloha-Editor/build/r.js -o ./build-aloha-for-ductus.js

# compile aloha.css
# this will probably trigger some warnings about CSS imports missing (aloha-sidebar.css and repository-browser.css), they're on purpose,
# to prevent problems when deploying code with Django's manage.py collectstatic that would look for files that do not exist.
cp aloha-css-for-ductus.css_template aloha/css/aloha-css-for-ductus.css
node ../../../../submodules/Aloha-Editor/build/r.js -o cssIn=aloha/css/aloha-css-for-ductus.css out=aloha/css/aloha.css optimizeCss=standard
# remove original css files after compiling them into aloha.css so they don't trigger errors in the django collectstatic stage
echo "removing CSS source files"
rm aloha/css/aloha-*
echo "removing any @import statements left in aloha.css"
sed -i 's/@import[^;]*;//g'  aloha/css/aloha.css
