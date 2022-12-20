# statrep

Status report for all controlled nodes: monitor failed systemd units
and high-priority entries in the system journal

# Usage

All sensitive/admin's data is kept in the file `config.sh`, which is not
included in the repo (it is in `.gitignore`). In the root directory of
the repo, create this file with the definition of the following
variables:
```bash
MASTER_SERVER="..."  # hostname or IP of the master server 
MASTER_PORT=0        # http port on master server
PATH_GET="..."       # server path for GET method
PATH_POST="..."      # server path for POST method
INVENTORY_FILE="..." # path to ansible inventory file
```
When running `install-server.sh` and `install-clients.sh` below, the
contents of this config will be copied into appropriate source files.

NOTE: This config is copied both into shell and python scripts, so it is
mandatory that there are no spaces around `=`.



## Server

Install/update the server:
```bash
# make sure to run from the repo's root directory
./install-server.sh
```

Dependencies:
- `python-psycopg2` to store/access entries in PostgreSQL
  (automatically installed if absent)


## Clients

Install/update clients:
```bash
# make sure to run from the repo's root directory
./install-clients.sh [nodes]
```
All managed clients should be listed in ansible inventory under the
`statrep` group. The optional `nodes` argument might be used to apply
the playbook to a different group of nodes (should also be defined in
the inventory file).

Dependencies:
- `curl` (automatically installed if absent)

