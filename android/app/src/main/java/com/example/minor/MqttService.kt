package com.example.minor

import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import android.widget.Toast
import info.mqtt.android.service.MqttAndroidClient
import org.eclipse.paho.client.mqttv3.*

class MqttService : Service() {
    private lateinit var mqttAndroidClient: MqttAndroidClient
    private val serverUri = "tcp://192.168.146.179:1883"
    private val clientId = "AndroidClient"
//    private val subscriptionTopic = listOf("daq", "esp/devices")
    //                                     helmet 012, JSON

    private val subscriptionTopic = "esp/devices"
    inner class LocalBinder : Binder() {
        fun getService(): MqttService = this@MqttService
    }

    override fun onBind(intent: Intent?): IBinder {
        return LocalBinder()
    }

    // Constants for publishing messages
    private val PUBLISH_TOPIC = "testTopic"  // Change this to your desired publish topic
    private val PUBLISH_MESSAGE = "Hello, MQTT!"  // Change this to the message you want to publish


    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        mqttAndroidClient = MqttAndroidClient(applicationContext, serverUri, clientId)
        setupMqttClient()
        return START_STICKY
    }

    private fun setupMqttClient() {
        val mqttConnectOptions = MqttConnectOptions().apply {
            isAutomaticReconnect = true
            isCleanSession = false
            connectionTimeout = 10
            keepAliveInterval = 60
        }

        mqttAndroidClient.connect(mqttConnectOptions, null, object : IMqttActionListener {
            override fun onSuccess(asyncActionToken: IMqttToken) {
                subscribeToTopic()
            }

            override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                Toast.makeText(this@MqttService, "Failed to connect: $exception", Toast.LENGTH_LONG).show()
            }
        })

        mqttAndroidClient.setCallback(object : MqttCallback {
            override fun messageArrived(topic: String, message: MqttMessage) {
                val payload = message.toString()

                // Broadcast the message
                val intent = Intent("com.example.minor.MQTT_MESSAGE")
                intent.putExtra("topic", topic)
                intent.putExtra("message", payload)
                sendBroadcast(intent)
            }

            override fun connectionLost(cause: Throwable?) {
                // Handle connection loss
            }

            override fun deliveryComplete(token: IMqttDeliveryToken?) {
                // Handle message delivery completion
            }
        })
    }

    private fun subscribeToTopic() {
        mqttAndroidClient.subscribe(subscriptionTopic, 0, null, object : IMqttActionListener {
            override fun onSuccess(asyncActionToken: IMqttToken) {
                Toast.makeText(this@MqttService, "Subscribed to $subscriptionTopic", Toast.LENGTH_SHORT).show()
            }

            override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                Toast.makeText(this@MqttService, "Subscription failed", Toast.LENGTH_SHORT).show()
            }
        })
    }

    fun publishMessage(topic: String, message: String) {
        if (mqttAndroidClient.isConnected) {
            try {
                val mqttMessage = MqttMessage()
                mqttMessage.payload = message.toByteArray()
                mqttAndroidClient.publish(topic, mqttMessage)
            } catch (e: MqttException) {
                e.printStackTrace()
                Toast.makeText(this, "Error Publishing: $e", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(this, "Not connected to MQTT broker", Toast.LENGTH_SHORT).show()
        }
    }
}
