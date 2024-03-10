#!/usr/bin/env bash

cd "$(dirname "$0")" || exit

mkdir -p alist
cd alist || exit

alist_version=${ALIST_VERSION:-"3.30.0"}

if [ ! -f alist ]; then
    echo "Install Alist Version: ${alist_version}."
    wget -q "https://github.com/alist-org/alist/releases/download/v${alist_version}/alist-linux-amd64.tar.gz"
    tar xzvf alist-linux-amd64.tar.gz
fi

rm -rf alist/data/ alist/test_dir/ alist/test_dir_dst/
./alist admin set 123456
sed -i '' 's/: 5244/: 5245/' data/config.json
./alist restart
