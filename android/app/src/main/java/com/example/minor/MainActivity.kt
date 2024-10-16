package com.example.minor

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.ImageButton
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private lateinit var mqttReceiver: BroadcastReceiver
    private val messageHandler = Handler(Looper.getMainLooper())

    private val elements = arrayOf("Light1", "Light2")
    private var currentIndex = 0 // Keeps track of the current index

    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        val serviceIntent = Intent(this, MqttService::class.java)
        startService(serviceIntent)

        val btnCurrentElement = findViewById<Button>(R.id.btnCurrentElement)
        val btnBackward = findViewById<ImageButton>(R.id.btnBackward)
        val btnForward = findViewById<ImageButton>(R.id.btnForward)

        // Initialize UI and buttons
        btnCurrentElement.text = elements[currentIndex]
        btnBackward.setOnClickListener { moveBackward(btnCurrentElement) }
        btnForward.setOnClickListener { moveForward(btnCurrentElement) }
        btnCurrentElement.setOnClickListener { selectButton(btnCurrentElement) }

        // Register the broadcast receiver
        mqttReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                val topic = intent?.getStringExtra("topic")
                val message = intent?.getStringExtra("message")

                messageHandler.post {
                        handleMqttMessage(topic, message)
                }
            }
        }
    }

    private fun handleMqttMessage(topic: String?, message: String?) {
        when (topic) {
            "daq" -> {
                when (message) {
                    "0" -> moveBackward(findViewById(R.id.btnCurrentElement))
                    "1" -> moveForward(findViewById(R.id.btnCurrentElement))
                    "2" -> selectButton(findViewById(R.id.btnCurrentElement))
                }
            }
            "esp/devices" -> {
                val payload = message.toString()

                // Assuming the payload contains a JSON string in the format {"esp1": ["light", "fan"]}
                try {
                    val jsonObject = JSONObject(payload)

                    // We don't know the keys (esp1, esp2, etc.) so we iterate over the keys dynamically
                    val iterator: Iterator<String> = jsonObject.keys()

                    // To store devices and their subtopics
                    val deviceMap = mutableMapOf<String, List<String>>()

                    // Iterate over each device (key) in the JSON object
                    while (iterator.hasNext()) {
                        val deviceId = iterator.next()
                        val subtopicsArray = jsonObject.getJSONArray(deviceId)

                        // Convert subtopics from JSONArray to a Kotlin List
                        val subtopicsList = mutableListOf<String>()
                        for (i in 0 until subtopicsArray.length()) {
                            subtopicsList.add(subtopicsArray.getString(i))
                        }

                        // Add the device and its subtopics to the map
                        deviceMap[deviceId] = subtopicsList
                    }

                    // Log or perform operations with the deviceMap
                    deviceMap.forEach { (deviceId, subtopics) ->
                        println("Device ID: $deviceId, Subtopics: $subtopics")
                        // Subscribe to subtopics dynamically
//                        subtopics.forEach { subtopic ->
//                            mqttService.subscribe("esp/$deviceId/$subtopic", 0)
//                        }
                    }

                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }


    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    override fun onResume() {
        super.onResume()
        // Register the receiver when activity is in the foreground
        val intentFilter = IntentFilter("com.example.minor.MQTT_MESSAGE")
        registerReceiver(mqttReceiver, intentFilter, RECEIVER_NOT_EXPORTED)
    }

    override fun onPause() {
        super.onPause()
        // Unregister the receiver when activity is not visible
        unregisterReceiver(mqttReceiver)
    }

    // Function to move backward
    private fun moveBackward(btnCurrentElement: Button) {
        if (currentIndex > 0) {
            currentIndex--
        } else {
            currentIndex = elements.size - 1 // Loop back to the last element
        }
        btnCurrentElement.text = elements[currentIndex]
    }

    // Function to move forward
    private fun moveForward(btnCurrentElement: Button) {
        if (currentIndex < elements.size - 1) {
            currentIndex++
        } else {
            currentIndex = 0 // Loop back to the first element
        }
        btnCurrentElement.text = elements[currentIndex]
    }

    private fun selectButton(btnCurrentElement: Button){
        val intent = Intent(this@MainActivity, MainActivity2::class.java)
        intent.putExtra("deviceName", elements[currentIndex])
        startActivity(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Unregister the receiver when the activity is destroyed
        unregisterReceiver(mqttReceiver)
    }
}
