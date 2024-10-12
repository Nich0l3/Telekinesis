sudo apt install \
mosquitto mosquitto-clients avahi-daemon avahi-utils libnss-mdns \
-y

sudo cp dep/device-conf/avahi-daemon.conf /etc/avahi/ 
sudo cp dep/device-conf/mqtt.service /etc/avahi/services/  
