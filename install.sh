sudo apt-get install -y npm
sudo npm install pm2@next -g
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u pi --hp /home/pi
pm2 start game.sh
pm2 save