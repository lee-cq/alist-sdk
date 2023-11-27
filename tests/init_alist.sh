#!/usr/bin/env bash

cd "$(dirname "$0")" || exit

mkdir -p alist
cd alist || exit

if [ ! -f alist ]; then
    wget -q https://github.com/alist-org/alist/releases/download/v3.29.0/alist-linux-amd64.tar.gz
    tar xzvf alist-linux-amd64.tar.gz
fi

rm -rf alist/data/ alist/test_dir/ alist/test_dir_dst/
./alist admin set 123456
./alist restart
