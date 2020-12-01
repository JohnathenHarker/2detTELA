#!/bin/bash

# download curl
echo downloading curl
sudo apt install curl

# download and copile spot
echo downloading spot
curl -o spot-2.9.4.tar.gz https://www.lrde.epita.fr/dload/spot/spot-2.9.4.tar.gz -fsSL
tar -zxvf spot-2.9.4.tar.gz
cd spot-2.9.4
./configure  --enable-max-accsets=256

echo making spot; this may take some time
make
make install

cd ..

# run compile.sh
echo compiling 2detTELA
./compile.sh

echo finished installation
