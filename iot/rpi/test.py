import paho.mqtt.client as mqtt_client
import time

def on_message(client, userdata, message):
    print(f"\nreceived message: {message.payload.decode()}\non topic: {message.topic}\n\n")

client = mqtt_client.Client()

client.on_message = on_message

broker_address = "eeg.local"
client.connect(broker_address, port=1883)

topic = "testTopic"
client.subscribe(topic)

client.loop_start()

try:
    print("\Broker is running. You can now publish messages.\n")
    
    # Publish messages in a loop
    while True:
        message = input("\nEnter a message to publish (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        client.publish(topic, message)
        time.sleep(1)



except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Stop the loop and disconnect from the broker
    client.loop_stop()
    client.disconnect()


