import time
import paho.mqtt.client as mqtt

def on_publish(client, userdata, mid):
    print("message published")

client = mqtt.Client("rpi_client2") #this name should be unique
client.on_publish = on_publish
# connect to broker
client.connect('192.168.102.170',1883)
# start a new thread
client.loop_start()

topic1 = 'eeg-1/light'

while True:
    try:

        k = int(input('Enter light state: '))
        msg =str(k)
        pubMsg = client.publish(
            topic=topic1,
            payload=msg.encode('utf-8'),
            qos=0,
        )

        pubMsg.wait_for_publish()
        print(pubMsg.is_published())
    
    except Exception as e:
        exit(1)

