# Nautilus

Automation tools for deploying blockchain networks

## Prerequisites
Prior to using this script, it's assumed that docker is installed on the host 

This script builds and deploys a conseil, postgres, and/or tezos container.  In the repo, there is provided a default configuration for all three containers.  These configuration values can be changed, it's advisable to copy the config folder to another location so that the original can be kept intact for reference purposes.  

The default network for tezos is alphanet, and this setting is stored in https://github.com/Cryptonomic/Nautilus/blob/master/docker/config/local/tezos/tezos_network.txt This text file only contains one word, currently it's "alphanet".  However, it can be changed to mainnet or zeronet.  



