# Nautilus Core

Naultilus Core is a tool to automate running Tezos Nodes. It allows customization of the most important node features, and easily running multiple nodes, along with different integrations to simplfy node interactions.

With each Node in Archive mode, you can also start an instance of [Conseil](https://github.com/Cryptonomic/Conseil) and [Arronax](https://arronax.io).

## Prerequisites:

You need to have `wget`, `git`, `python3`, and `pip3` installed.

The app runs inside a python `venv` so it will not add anything to your system environment.

## Running Instructions:

Clone the project, and run `./setup_workspace.sh`, which will download docker images, and build Arronax docker images for the different networks.

After setup, you can run `start.sh` in the root directory of the project, and visit https://localhost:4104 to see the running UI.

We recommend that you do NOT interact with the nodes without the UI, as this can lead to discrepancies between your system, and the script.

Please only start and stop nodes from the UI.

Please respect the nodes, and the hard work they do. 

## Troubleshooting

If there is a node which is shown to be running on the app, but is not actually running on your computer, you can click "restart" to resync the UI with your computer.

## Uninstall / Cleanup:

Deleting the repository will delete all of the locally stored data.

Docker images will be generated, which can be removed using docker's CLI. All of the images generated have the names `conseil-api-foo`, `conseil-lorre-foo`, or `arronax-foo` where `foo` is the name of the nodes installed.

