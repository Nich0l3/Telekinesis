sudo apt install \
mosquitto mosquitto-clients avahi-daemon avahi-utils libnss-mdns \
gunicorn nginx\
-y

sudo cp dep/device-conf/avahi-daemon.conf /etc/avahi/ 
sudo cp dep/device-conf/mqtt.service /etc/avahi/services/  

echo allow_anonymous true >> /etc/mosquitto/mosquitto.conf
echo listener 1883 >> /etc/mosquitto/mosquitto.conf
