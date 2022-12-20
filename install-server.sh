#!/usr/bin/env bash

mkdir -p ./tmp

echo "Copying statrep-server.py to tmp/"
cp server/statrep-server.py tmp/statrep-server.py

# insert the content of config.py into server/statrep-server.py
echo "Inserting contents of config.sh into tmp/statrep-server.py"
sed -i -e '/# sed imports config here/r./config.sh' tmp/statrep-server.py

echo "Reading config.sh"
source ./config.sh

echo "Running ansible playbook"
ansible-playbook -K server/server.yaml -i "$MASTER_SERVER",

