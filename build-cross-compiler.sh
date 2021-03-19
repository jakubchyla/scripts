#! /usr/bin/env bash

pushd

BINUTILS_URL="https://ftp.gnu.org/gnu/binutils/binutils-2.34.tar.xz"
BINUTILS_FILENAME=`echo $BINUTILS_URL | grep -P --only-matching "binutils-\d\.\d\d"`
GCC_URL="https://ftp.gnu.org/gnu/gcc/gcc-9.3.0/gcc-9.3.0.tar.xz"
GCC_FILENAME=`echo $GCC_URL | grep -P --only-matching "gcc-\d\.\d\.\d" | head -n 1`

if ! [ -d ~/opt/cross_compiler ];then mkdir -p ~/opt/cross_compiler; fi

export PREFIX="$HOME/opt/cross_compiler"
export TARGET="i686-elf"
export PATH="$PREFIX/bin:$PATH"


# build binutils
cd /tmp
curl -o $BINUTILS_FILENAME.tar.xz $BINUTILS_URL
tar xJf $BINUTILS_FILENAME.tar.xz

cd $BINUTILS_FILENAME
mkdir build; cd build
../configure --target=$TARGET --prefix="$PREFIX" --with-sysroot \
    --disable-nls --disable-werror
make -j `nproc`
make -j `nproc` install


# build gcc
cd /tmp

curl -o $GCC_FILENAME.tar.xz $GCC_URL
tar xJf $GCC_FILENAME.tar.xz

cd $GCC_FILENAME
mkdir build; cd build
../configure --target=$TARGET --prefix="$PREFIX" --disable-nls \
    --enable-languages=c,c++ --without-headers
make -j `nproc` all-gcc
make -j `nproc` all-target-libgcc
make -j `nproc` install-gcc
make -j `nproc` install-target-libgcc

popd
