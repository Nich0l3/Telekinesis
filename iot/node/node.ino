#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Change dev ID for every new node
#define                 esp1 // esp2
#define DEVID           "esp2"
#define WIFI_SSID       "Pixel"
#define WIFI_PASSWORD   ""
#define THR             -30
#define LOW              1
#define HIGH             0
#define TRIG             D6 

// MQTT Broker settings
const char* mqtt_server = "eeg.local";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// MQTT Topics
String mqtt_topic_0_str = String(DEVID) + "/light";
const char* mqtt_topic_0 = mqtt_topic_0_str.c_str();// const char* mqtt_topic_1 = "esp1/fan";
const char* device_topic = "esp/devices";

// Function Prototypes
void connectToWiFi();
void connectToMQTTBroker();
void publishConnectedDevices();
void checkWiFiSignal();
void broadcastDisconnect();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void set_state(uint8_t pin, uint8_t state);

// WiFi signal checking interval
unsigned long lastSignalCheck = 0;
const unsigned long signalCheckInterval = 5000;  // Check every 5 seconds
int sig_strength;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(TRIG,OUTPUT);

  set_state(LED_BUILTIN,LOW);
  set_state(TRIG,1);

  mqtt_client.setServer(mqtt_server, mqtt_port);
  mqtt_client.setCallback(mqttCallback);

  connectToMQTTBroker();
}

void loop() {
  if (!mqtt_client.connected()) {
    connectToMQTTBroker();
  }
     checkWiFiSignal();
  mqtt_client.loop();
  delay(500);     // Adjust the delay as needed
}

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  Serial.println("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    int n = WiFi.scanNetworks();
    Serial.print(".");
    for (int i = 0; i < n; ++i) {
      if (WiFi.SSID(i) == WIFI_SSID && WiFi.RSSI(i) > THR) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
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
  set_state(BUILTIN_LED, HIGH);
}

void subscribeToTopics() {
  mqtt_client.subscribe(mqtt_topic_0);
  mqtt_client.subscribe(device_topic);
}

void connectToMQTTBroker() {
  while (!mqtt_client.connected()) {
  // Initial wifi check
    while (WiFi.status() != WL_CONNECTED) {
      connectToWiFi();
    }

    String client_id = "esp8266-client-" + String(WiFi.macAddress());
    Serial.printf("Connecting to MQTT Broker as %s.....\n", client_id.c_str());
    if (mqtt_client.connect(client_id.c_str())) {
      Serial.println("Connected to MQTT broker");
      subscribeToTopics();
      publishConnectedDevices();
    } else 
       //break;
    {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }

  //  Threshold check
    checkWiFiSignal();
  }
}

void broadcastDisconnect(){
  // Array to send
  String Data = "disconnected";
  const int Size = sizeof(Data);

  // Create a JSON document
  StaticJsonDocument<200> jsonDoc;

  // Populate the JSON array
  JsonArray jsonArray = jsonDoc.createNestedArray(DEVID);
  
  jsonArray.add(Data);

  // Serialize the JSON object to a string
  char jsonBuffer[512];
  serializeJson(jsonDoc, jsonBuffer);

  // Publish the JSON string to the MQTT topic
  mqtt_client.publish(device_topic, jsonBuffer);
}

void checkWiFiSignal() {
  if (WiFi.status() == WL_CONNECTED) {
    int rssi = WiFi.RSSI();
    Serial.print("Current WiFi RSSI: ");
    Serial.println(rssi);
    if (rssi < THR) {
      Serial.println("WiFi signal strength is low. Disconnecting...");
      if (mqtt_client.connected()) {
        broadcastDisconnect();
        Serial.println("Disconnect message sent. Waiting for confirmation...");
        delay(500);  // Give time for the MQTT message to be transmitted
      }
      WiFi.disconnect();
      set_state(BUILTIN_LED, LOW);
      Serial.println("Disconnected from WiFi.");
    }
  }
}

void set_state(uint8_t pin,uint8_t state) {
  digitalWrite(pin, state);
}

// this function is called when both wifi and mqtt is successfully connected
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  
  String messageTemp;
  for (unsigned int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }
  Serial.println(messageTemp);

  if (messageTemp == "0") {
    Serial.println("switched to LOW");
    set_state(TRIG, 1);
  } else if (messageTemp == "1") {
    Serial.println("switched to HIGH");
    set_state(TRIG, 0);
  }
  Serial.println();
  // checkWiFiSignal();
  Serial.println("-----------------------");
}

void publishConnectedDevices() {
  // Connected devices array
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

