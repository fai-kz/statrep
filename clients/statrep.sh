#!/usr/bin/env bash

# sed imports config here. DO NOT DELETE OR MODIFY THIS LINE!


# sleep for random number of seconds (from 1 to 200 sec),
# so that requests to server from all clients are on average uniform in time
sleep $((RANDOM % 200))

url="http://${MASTER_SERVER}:${MASTER_PORT}${PATH_POST}"
jfile="/tmp/jcursor.tmp"

function join_by {
    local d=${1-} f=${2-}
    if shift 2; then
        printf %s "$f" "${@/#/$d}"
    fi
}


failed=""

systemctl -q is-system-running
# if there are failed units, list them
# and also try to restart (depending on server's hint)
if [ $? -ne 0 ]; then

    failed=$(systemctl --failed --no-pager --quiet --no-legend --plain | cut -d' ' -f1 | paste -sd " " -)

    # join elements into ones string using commas and quotes
    failed=$(join_by "\", \"" ${failed[@]})
    failed="\"$failed\""

    autoheal=$(curl -X POST \
         -H 'Content-Type: application/json' \
         -d '{"host": "'$(hostname)'", "failed": ['"$failed"']}' \
         "$url")

    if [ $autoheal = "YES" ]; then
        # try to reset failed units
        systemctl reset-failed
    fi
fi

jevents=""

if [ ! -f "$jfile" ]; then
    touch $jfile
    jevents=$(journalctl -q -p 3 --cursor-file=$jfile --since="1 hour ago" --output-fields=MESSAGE,PRIORITY,SYSLOG_IDENTIFIER -o json --no-pager | paste -sd "," -)
else
    jevents=$(journalctl -q -p 3 --cursor-file=$jfile --output-fields=MESSAGE,PRIORITY,SYSLOG_IDENTIFIER -o json --no-pager | paste -sd "," -)
fi


if [ "$jevents" ]; then

    sleep 2
    jevents='{"host": "'$(hostname)'", "journal": ['"$jevents"'] }'
    echo "$jevents" > /tmp/jevents.tmp
    curl -X POST \
         -H 'Content-Type: application/json' \
         -d @/tmp/jevents.tmp \
         "$url"

fi

