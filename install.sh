#!/usr/bin/env bash
sudo apt-get install -y npm
sudo npm install pm2@next -g
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u pi --hp /home/pi
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 1M
pm2 set pm2-logrotate:retain 5
pm2 start game.sh
pm2 save