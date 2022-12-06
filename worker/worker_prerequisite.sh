#!/bin/bash
wget https://download.pytorch.org/models/googlenet-1378be20.pth
wget https://raw.githubusercontent.com/Superkakayong/MarvelousNet/master/worker/imagenet_label.json
wget https://raw.githubusercontent.com/Superkakayong/MarvelousNet/master/worker/worker.py
wget https://raw.githubusercontent.com/Superkakayong/MarvelousNet/master/worker/requirements.txt

sudo apt-get update
sudo apt-get install -y python3-pip
sudo apt-get install -y libjpeg-dev zlib1g-dev
pip3 --no-cache-dir install torch==1.10.0+cpu torchvision==0.11.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
pip3 install -r requirements.txt