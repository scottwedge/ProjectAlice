#!/usr/bin/env bash

cd ~ || exit

if [[ -d "seeed-voicecard" ]]; then
  rm -rf seeed-voicecard
fi

git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard || exit
chmod +x ./install.sh
./install.sh

rm -rf seeed-voicecard

sleep 1
