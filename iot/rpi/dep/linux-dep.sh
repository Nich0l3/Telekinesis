sudo apt install neovim xclip\
 mosquitto mosquitto-clients avahi-daemon avahi-utils libnss-mdns \
 gunicorn nginx\
 -y

sudo cp device-conf/avahi-daemon.conf /etc/avahi/ 
sudo cp device-conf/mqtt.service /etc/avahi/services/  
cp device-conf/.bash_aliases ~/

echo allow_anonymous true >> /etc/mosquitto/mosquitto.conf
echo listener 1883 >> /etc/mosquitto/mosquitto.conf
