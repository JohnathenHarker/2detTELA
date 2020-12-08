#!/bin/bash


# download and copile spot
curl -o spot-2.9.4.tar.gz https://www.lrde.epita.fr/dload/spot/spot-2.9.4.tar.gz -fsSL
tar -zxvf spot-2.9.4.tar.gz
cd spot-2.9.4
./configure --prefix ~/usr --enable-max-accsets=256 --disable-python

make
make install

cd ..

# run compile.sh
./compile.sh

# install psutil
python3 -m pip install psutil

echo finished installation of 2detTELA
