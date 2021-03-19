#! /bin/bash

if [ ! $(which "dnf") ]; then
    printf "%s\n" "DNF not found" 
                  "This scripts only supports fedora"
    exit -1 
else
    sudo dnf -y builddep emacs
    sudo dnf -y install git autogen
fi

if [ -z $1 ]; then
    printf "%s\n" "No path specified"
    exit -1
fi

BUILD_DIR="$1"

if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p "$BUILD_DIR"
    fi

git clone --depth=1 https://github.com/emacs-mirror/emacs.git "$BUILD_DIR"
pushd
./autogen.sh
./configure --with-json --with-modules --with-harfbuzz --with-compress-install \
            --with-threads --with-included-regex --with-zlib 
make -j `nproc`

popd
