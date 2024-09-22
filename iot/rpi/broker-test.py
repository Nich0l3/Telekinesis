import sys
from paho.mqtt import client as mqtt_client

client = mqtt_client.Client()

if client.connect("localhost",1883,60) != 0 :
    print('Couldn\'t connect to mqtt broker')
    sys.exit(1)

client.publish("testTopic","Hi, paho mqtt client works fine", 0)
client.disconnect()
