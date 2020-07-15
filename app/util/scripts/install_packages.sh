#!/bin/bash

#if [ "$1" == "-l" ]; then
    # LINUX INSTALLATION

    # Opam installation
    yes "" | sh <(curl -sL https://raw.githubusercontent.com/ocaml/opam/master/shell/install.sh)

    # Install rustup
    yes "" | curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env

    # Use rustup to install rust
    rustup toolchain install 1.39.0
    rustup default 1.39.0
    source $HOME/.cargo/env
#else
#    # MACOS INSTALLATION
#
#    # Install macOS homebrew package manager
#    yes "" | /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
#
#    # Install macOS developer tools
#    xcode-select --install
#
#    # Install tezos package dependencies
#    yes "" | brew install hidapi libev
#    yes "" | brew install gpatch
#    yes "" | brew install opam
#    source $HOME/.cargo/env
#fi