#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define WIFI_SSID       "Pixel"
#define WIFI_PASSWORD   ""  
#define LOW             1
#define HIGH            0

// WiFi settings
const char *ssid      = WIFI_SSID;        // Replace with your WiFi name
const char *password  = WIFI_PASSWORD;    // Replace with your WiFi password

// MQTT Broker settings
const char* mqtt_server = "192.168.102.170";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// MQTT misc
const char* mqtt_topic = "eeg-1/light";

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to the WiFi network");
}

void connectToMQTTBroker() {
    while (!mqtt_client.connected()) {
        String client_id = "esp8266-client-" + String(WiFi.macAddress());
        Serial.printf("Connecting to MQTT Broker as %s.....\n", client_id.c_str());
        if (mqtt_client.connect(client_id.c_str())) {
            Serial.println("Connected to MQTT broker");
            mqtt_client.subscribe(mqtt_topic);
        } else {
            Serial.print("Failed to connect to MQTT broker, rc=");
            Serial.print(mqtt_client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void set_state(uint8_t state){
  digitalWrite(LED_BUILTIN,state);
  digitalWrite(D6,state);
  digitalWrite(D7,state);
}

String messageTemp = "";

void mqttCallback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Message received on topic: ");
    Serial.println(topic);
    Serial.print("Message:");
    char messageTemp;

    for (unsigned int i = 0; i < length; i++) {
        messageTemp += (char)payload[i];
        Serial.print(messageTemp);
        Serial.println();
    }
    
    if ((String)topic == mqtt_topic){
      if(messageTemp == '0'){
          Serial.println("switched to LOW");
          set_state(LOW);

      } else if (messageTemp == '1'){
          Serial.println("switched to HIGH");    
          set_state(HIGH);
      }
    }
    Serial.println();
    Serial.println("-----------------------");
}

void setup() {
    Serial.begin(115200);
    
    pinMode(LED_BUILTIN,OUTPUT);
    pinMode(D6,OUTPUT);
    pinMode(D7,OUTPUT);
  //  set_state(LOW);
    
    connectToWiFi();
    
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    
    connectToMQTTBroker();
}

void loop() {
    if (!mqtt_client.connected()) {
        connectToMQTTBroker();
    }
    mqtt_client.loop();
}
