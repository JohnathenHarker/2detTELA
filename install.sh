#!/bin/bash

# download curl
sudo apt install curl
sudo apt-get install build-essential

# download and copile spot
curl -o spot-2.9.4.tar.gz https://www.lrde.epita.fr/dload/spot/spot-2.9.4.tar.gz -fsSL
tar -zxvf spot-2.9.4.tar.gz
cd spot-2.9.4
./configure  --enable-max-accsets=256 --disable-python

make
sudo make install
sudo ldconfig

cd ..

# run compile.sh
./compile.sh

echo finished installation of 2detTELA
