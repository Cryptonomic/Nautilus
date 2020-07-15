# tezos-scripting

This is a tool to automate the setup and installation of multiple Tezos nodes on the same machine, using a simple GUI.

This is a work in progress, don't kill me. 

## Setup Instructions:

Run `setup_workspace.sh` before doing anything, this will downoad tezos, and install its dependencies, along with those for Conseil, and any of the other features built into this tool.

This will ask for root privilege when running, which you should provice ONLY AFTER ENSURING THAT THE SCRIPT YOU ARE RUNNING IS DOING AS EXPECTED!

## Running Instructions:

After setup, you can just run `start.sh` in the root directory of the project, and visit https://localhost:5000 to see the running UI.

We recommend that you do NOT interact with the nodes without the UI, as this can lead to discrepancies in the script.

Please only start and stop nodes from the UI.

## Uninstall / Cleanup:

Deleting the repository will delete all of the localy stored data.

Installed dependencies using apt and PIP can be installed user their respective uninstall tools.

Docker images will be generated, which can be removed using docker's CLI. All of the images generated have the names `conseil-api-foo`, `conseil-lorre-foo`, or `arronax-foo` where `foo` is the name of the nodes installed.

