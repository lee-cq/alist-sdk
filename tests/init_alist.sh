#!/usr/bin/env bash

cd "$(dirname "$0")" || exit

mkdir -p alist
cd alist || exit

wget -q https://github.com/alist-org/alist/releases/download/v3.28.0/alist-linux-amd64.tar.gz
tar xzvf alist-linux-amd64.tar.gz

./alist admin set 123456
./alist start
