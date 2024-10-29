#include <PubSubClient.h>
//#include <ESPmDNS.h>
#include "cred.h"
#include <ArduinoJson.h>

#define MY_SSID "Pixel"
#define THR -40

#define ESP8266

#ifdef ESP32
#include <WiFi.h>
#endif
#ifdef ESP8266
#include <ESP8266WiFi.h>
#define LOW 1
#define HIGH 0
#endif

#define DEVID "esp2"

// WiFi settings
const char* ssid = "Pixel";
const char* password = "";

// MQTT Broker settings
const char* mqtt_server = "bcibroker.local";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// MQTT misc
const char* mqtt_topic_0 = "esp2/light";
const char* mqtt_topic_1 = "esp1/fan";
const char* device_topic = "esp/devices";


int sig_strength;


void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Checking WiFi signal for first time...");

    int n = WiFi.scanNetworks();
    for (int i = 0; i < n; ++i) {
      if (WiFi.SSID(i) == MY_SSID && WiFi.RSSI(i) > THR) {
        WiFi.begin(ssid, password);
        Serial.println("Connecting to WiFi");
        Serial.print(WiFi.SSID(i));
        Serial.print(" (");
        Serial.print(WiFi.RSSI(i));
        Serial.println(")");
        Serial.println();
        while (WiFi.status() != WL_CONNECTED) {
          Serial.print('.');
          delay(1000);
        }
        break;
      }
    }
  }
  Serial.println("\nConnected to the WiFi network");
}

void broadcastDisconnect(){
  // Array to send
  String arrayData[] = {"disconnected"};
  const int arraySize = sizeof(arrayData) / sizeof(arrayData[0]);

  // Create a JSON document
  StaticJsonDocument<200> jsonDoc;

  // Populate the JSON array
  JsonArray jsonArray = jsonDoc.createNestedArray(DEVID);
  for (int i = 0; i < arraySize; i++) {
    jsonArray.add(arrayData[i]);
  }

  // Serialize the JSON object to a string
  char jsonBuffer[512];
  serializeJson(jsonDoc, jsonBuffer);

  // Publish the JSON string to the MQTT topic
  mqtt_client.publish(device_topic, jsonBuffer);
}


void disconnectFromWiFi() {
  Serial.println("Checking WiFi signal 2nd time...");
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; ++i) {
    if (WiFi.SSID(i) == MY_SSID && WiFi.RSSI(i) < THR) {
      Serial.println("WiFi signal strength is low. Disconnecting...");

      if (mqtt_client.connected()) {
        broadcastDisconnect();
        Serial.println("Disconnect message sent. Waiting for confirmation...");
        
        // Wait for the message to be sent before disconnecting
        delay(500);  // Give time for the MQTT message to be transmitted
      }

      WiFi.disconnect();
      Serial.println("Disconnected from WiFi.");
      break;
    }
  }

}


void subscribeToTopics() {
  mqtt_client.subscribe(mqtt_topic_0);
  mqtt_client.subscribe(mqtt_topic_1);
  mqtt_client.subscribe(device_topic);
}

void connectToMQTTBroker() {
  while (!mqtt_client.connected()) {

    while (WiFi.status() != WL_CONNECTED) {
      connectToWiFi();
    }

    String client_id = "esp8266-client-" + String(WiFi.macAddress());
    Serial.printf("Connecting to MQTT Broker as %s.....\n", client_id.c_str());
    if (mqtt_client.connect(client_id.c_str())) {
      Serial.println("Connected to MQTT broker");
      subscribeToTopics();
      publishArray();

    } else 
       //break;
    {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
// int LED_BUILTIN = 2;
void set_state(uint8_t state) {
  digitalWrite(LED_BUILTIN, state);
}

String messageTemp = "";

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  char messageTemp;

  for (unsigned int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
    Serial.print(messageTemp);
    Serial.println();
  }

  // if ((String)topic == mqtt_topic_0){
  if (messageTemp == '0') {
    Serial.println("switched to LOW");
    set_state(LOW);

  } else if (messageTemp == '1') {
    Serial.println("switched to HIGH");
    set_state(HIGH);
  }
  // }
  Serial.println();
  Serial.println("-----------------------");
}

void publishArray() {
  // Array to send
  String arrayData[] = { "light"};
  const int arraySize = sizeof(arrayData) / sizeof(arrayData[0]);

  // Create a JSON document
  StaticJsonDocument<200> jsonDoc;

  // Populate the JSON array
  JsonArray jsonArray = jsonDoc.createNestedArray(DEVID);
  for (int i = 0; i < arraySize; i++) {
    jsonArray.add(arrayData[i]);
  }

  // Serialize the JSON object to a string
  char jsonBuffer[512];
  serializeJson(jsonDoc, jsonBuffer);

  // Publish the JSON string to the MQTT topic
  mqtt_client.publish(device_topic, jsonBuffer);
}



void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  //   pinMode(D6,OUTPUT);
  //   pinMode(D7,OUTPUT);
  set_state(LOW);

  //    startmDNS();

  mqtt_client.setServer(mqtt_server, mqtt_port);
  mqtt_client.setCallback(mqttCallback);

  connectToMQTTBroker();
}

unsigned long lastSignalCheck = 0;
const unsigned long signalCheckInterval = 5000;  // Check every 30 seconds

void loop() {
  if (!mqtt_client.connected()) {
    connectToMQTTBroker();
  }
  
  mqtt_client.loop();

  unsigned long currentMillis = millis();
  // if (currentMillis - lastSignalCheck >= signalCheckInterval) {
  //   lastSignalCheck = currentMillis;
  // }
  disconnectFromWiFi();

  }