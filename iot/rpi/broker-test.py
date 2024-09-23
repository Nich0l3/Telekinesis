import paho.mqtt.client as mqtt_client

def on_message(client, userdata, message):
    print(f"\nReceived message: {message.payload.decode()} on topic: {message.topic}")

client = mqtt_client.Client()

client.on_message = on_message

broker_address = "eeg.local"
client.connect(broker_address, port=1883)

topic = "testTopic"
client.subscribe(topic)

client.loop_start()

try:
    print("Subscriber is running. You can publish messages to the same topic.")
    
    # Publish messages in a loop
    while True:
        message = input("Enter a message to publish (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        client.publish(topic, message)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Stop the loop and disconnect from the broker
    client.loop_stop()
    client.disconnect()

