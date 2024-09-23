import time
import paho.mqtt.client as mqtt

def on_publish(client, userdata, mid):
    print("message published")

def home_automation(msg):
    
    if msg.isdigit() != 1 :
        print("Not a valid input")
        return

    pubMsg = client.publish(
            topic=topic1,
            payload=msg.encode('utf-8'),
            qos=0,
    )
    pubMsg.wait_for_publish()
    print( "Published" if (pubMsg.is_published()) else "Not Published")

client = mqtt.Client("rpi_client2") #this name should be unique
client.on_publish = on_publish
# connect to broker
client.connect('eeg.local',1883)
# start a new thread
client.loop_start()

topic1 = 'eeg-1/light'

while(True):
    try:
        # when conditions are met
        state = input('Enter light state:')
        home_automation(state)
    except Exception as e:
            print(e)
            time.sleep(1)
