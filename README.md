# tezos-scripting

This is a tool to automate the setup and installation of multiple Tezos nodes on the same machine, using a simple GUI.

This is a work in progress, don't kill me. 

## Prerequisistes:

You need to have `curl`, `wget`, `git`, `python3`, and `pip3` installed.

You also need to install `flask` using `pip3`.

I think that's it. Eventually there will be a `pip` requirements file, but until then, you're on you're own mate.

## Running Instructions:

After setup, you can just run `start.sh` in the root directory of the project, and visit https://localhost:5000 to see the running UI.

We recommend that you do NOT interact with the nodes without the UI, as this can lead to discrepancies in the script.

Please only start and stop nodes from the UI.

Please respect the nodes, and the hard work they do. 

## Uninstall / Cleanup:

Deleting the repository will delete all of the locally stored data.

Docker images will be generated, which can be removed using docker's CLI. All of the images generated have the names `conseil-api-foo`, `conseil-lorre-foo`, or `arronax-foo` where `foo` is the name of the nodes installed.

I'll probably create an uninstall button soon.

