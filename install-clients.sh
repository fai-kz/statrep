#!/usr/bin/env bash

mkdir -p ./tmp

echo "Copying statrep.sh to tmp/"
cp clients/statrep.sh tmp/statrep.sh

# insert the content of config.py into server/statrep-server.py
echo "Inserting contents of config.sh into tmp/statrep.sh"
sed -i -e '/# sed imports config here/r./config.sh' tmp/statrep.sh

echo "Reading config.sh"
source ./config.sh

if [ $# -eq 0 ]; then
    echo "Running ansible playbook for statrep group"
    ansible-playbook -i "$INVENTORY_FILE" -K clients/statrep.yaml 
else
    echo "Running ansible playbook for $1 group"
    ansible-playbook -i "$INVENTORY_FILE" -K clients/statrep.yaml --extra-vars "targetgroup=$1"
fi



