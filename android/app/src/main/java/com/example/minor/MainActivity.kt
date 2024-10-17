package com.example.minor

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
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

    private val handler = Handler(Looper.getMainLooper())

    private val devicesList = mutableMapOf<String, List<String>>()
    private var espDevices = mutableListOf<Pair<String, String>>() // Mutable list for (ESP, Device)

    private var currentIndex = 0 // Keeps track of the current index in the combined list

    private lateinit var btnMoveLeft: ImageButton
    private lateinit var btnMoveRight: ImageButton

    private var isBtnLeftVisible = true
    private var isBtnRightVisible = true

    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        val serviceIntent = Intent(this, MqttService::class.java)
        startService(serviceIntent)

        btnMoveLeft = findViewById(R.id.btnBackward)
        btnMoveRight = findViewById(R.id.btnForward)

        startFlicker10Hz()
        startFlicker15Hz()

        espDevices.add("default" to "NO DEVICES")

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

            "DAQ" -> {
                if(espDevices.isNotEmpty()){
                    when (message) {
                        "0" -> {
                            moveBackward(findViewById(R.id.btnCurrentElement))
                            Toast.makeText(this,"Received 0: Moved Left",Toast.LENGTH_SHORT).show()
                        }
                        "1" -> {
                            moveForward(findViewById(R.id.btnCurrentElement))
                            Toast.makeText(this,"Received 1: Moved Right",Toast.LENGTH_SHORT).show()
                        }
                        "2" -> {
                            selectButton(findViewById(R.id.btnCurrentElement))
                            Toast.makeText(this,"Received 2: Device Selected",Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            }

            "esp/devices" -> {
                val payload = message.toString()

                // Assuming the payload contains a JSON string in the format {"esp1": ["light", "fan"]}
                try {
                    val jsonObject = JSONObject(payload)

                    // Iterate over the keys (ESP ids) dynamically
                    val iterator: Iterator<String> = jsonObject.keys()

                    // Iterate over each ESP and its devices
                    while (iterator.hasNext()) {
                        val espId = iterator.next()
                        val devicesArray = jsonObject.getJSONArray(espId)

                        // Convert devices from JSONArray to a Kotlin List
                        val devices = mutableListOf<String>()

                        if(devicesArray.getString(0) == "disconnected"){
                            // Remove all elements from espDevices where the first value is espId
                            espDevices.removeAll { it.first == espId }
                            devicesList.remove(espId) // Also remove from the devices map

                            Toast.makeText(this,"$espId got disconnected",Toast.LENGTH_SHORT).show()

                            if(espDevices.isEmpty()){
                                espDevices.add("default" to "NO DEVICES" )
                            }
                        }
                        else{

                            espDevices.removeAll { it.first == "default" }
                            devicesList.remove("default")

                            for (i in 0 until devicesArray.length()) {
                                devices.add(devicesArray.getString(i))
                            }

                            // Add the ESP and its devices to the map and also populate the combined list
                            devicesList[espId] = devices
                            devices.forEach { device ->
                                espDevices.add(espId to device) // Add (ESP, Device) pairs
                            }
                            Toast.makeText(this,"$espId connected",Toast.LENGTH_SHORT).show()
                        }


                    }

                    // Initialize or update the UI only if the device list is not empty
                    if (espDevices.isNotEmpty()) {
                        initializeUI()
                    }

                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }

    private fun initializeUI() {
        currentIndex = 0
        val btnCurrentElement = findViewById<Button>(R.id.btnCurrentElement)
        val btnBackward = findViewById<ImageButton>(R.id.btnBackward)
        val btnForward = findViewById<ImageButton>(R.id.btnForward)

        // Set the first ESP-Device pair in the button text
        updateButtonUI(btnCurrentElement)

        // Set click listeners for forward and backward navigation
        btnBackward.setOnClickListener { moveBackward(btnCurrentElement) }
        btnForward.setOnClickListener { moveForward(btnCurrentElement) }
        btnCurrentElement.setOnClickListener { selectButton(btnCurrentElement) }
    }

    // Function to update the button UI with the current ESP-Device pair
    private fun updateButtonUI(button: Button) {
        val (espId, device) = espDevices[currentIndex]
        button.text = "$espId \n $device" // Display ESP and device
    }

    // Function to move backward in the device list
    private fun moveBackward(button: Button) {
        if (currentIndex > 0) {
            currentIndex--
        } else {
            currentIndex = espDevices.size - 1 // Loop back to the last element
        }
        updateButtonUI(button)
    }

    // Function to move forward in the device list
    private fun moveForward(button: Button) {
        if (currentIndex < espDevices.size - 1) {
            currentIndex++
        } else {
            currentIndex = 0 // Loop back to the first element
        }
        updateButtonUI(button)
    }

    // Function to handle button selection and navigate to the next activity
    private fun selectButton(button: Button) {
        val (espId, device) = espDevices[currentIndex]
        val intent = Intent(this@MainActivity, MainActivity2::class.java)
        intent.putExtra("espId", espId)
        intent.putExtra("deviceName", device)
        startActivity(intent)
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

    override fun onDestroy() {
        super.onDestroy()
        // Unregister the receiver when the activity is destroyed
        unregisterReceiver(mqttReceiver)
    }

    // Flicker ImageButton at 10Hz
    private fun startFlicker10Hz() {
        handler.postDelayed(object : Runnable {
            override fun run() {
                btnMoveLeft.visibility = if (isBtnLeftVisible)  View.INVISIBLE else View.VISIBLE
                isBtnLeftVisible = !isBtnLeftVisible
                handler.postDelayed(this, 50L) // 10 Hz = 50ms on + off
            }
        }, 50L)
    }

    // Flicker ImageButton at 15Hz
    private fun startFlicker15Hz() {
        handler.postDelayed(object : Runnable {
            override fun run() {
                btnMoveRight.visibility = if (isBtnRightVisible) View.INVISIBLE else View.VISIBLE
                isBtnRightVisible = !isBtnRightVisible
                handler.postDelayed(this, 34L) // 15 Hz = ~34ms on + off
            }
        }, 34L)
    }
}
