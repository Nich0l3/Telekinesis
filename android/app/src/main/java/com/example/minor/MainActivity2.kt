package com.example.minor

import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.ServiceConnection
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import android.widget.ToggleButton
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.json.JSONObject

class MainActivity2 : AppCompatActivity() {

    private lateinit var largeButton1: Button
    private lateinit var largeButton2: Button
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var mqttService: MqttService  // Declare the service variable
    private var isBound = false  // Track the service binding state

    // Flickering intervals in milliseconds
    private val flickerRate10Hz = 50L  // 10 Hz = 100ms on+off
    private val flickerRate15Hz = 34L   // 15 Hz = ~67ms

    private var isButton1Visible = true
    private var isButton2Visible = true

    private lateinit var mqttReceiver: BroadcastReceiver
    private val messageHandler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main2)

        val deviceSelected = intent.getStringExtra("deviceName")

        val deviceName = findViewById<TextView>(R.id.deviceNameTextView)
        deviceName.text = deviceSelected

        val toggleBtn = findViewById<ToggleButton>(R.id.stateToggleButton)
        toggleBtn.setOnCheckedChangeListener { _, isChecked ->
            if (isBound) {
                // Publish message based on toggle state
                val message = if (isChecked) "1" else "0" // 1 for ON, 0 for OFF
                mqttService.publishMessage("signal", message)
            } else {
                Toast.makeText(this, "Service not bound", Toast.LENGTH_SHORT).show()
            }
        }

        largeButton1 = findViewById(R.id.largeButton1)
        largeButton2 = findViewById(R.id.largeButton2)

        // Start flickering both buttons
        startFlicker10Hz()
        startFlicker15Hz()

        // Bind to the service
        Intent(this, MqttService::class.java).also { intent ->
            bindService(intent, connection, Context.BIND_AUTO_CREATE)
        }

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
            "signal" -> {
                when (message) {
                    "0" -> Toast.makeText(this, "Light Turned Off", Toast.LENGTH_SHORT).show()
                    "1" -> Toast.makeText(this, "Light Turned On", Toast.LENGTH_SHORT).show()
                    "2" -> finish() // Go back to MainActivity
                }
            }
        }
    }

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as MqttService.LocalBinder
            mqttService = binder.getService() // Get the service instance
            isBound = true
        }

        override fun onServiceDisconnected(name: ComponentName?) {
//            mqttService = null
            isBound = false
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

    // Flicker button 1 at 10Hz
    private fun startFlicker10Hz() {
        handler.postDelayed(object : Runnable {
            override fun run() {
                // Toggle button visibility or background color
                if (isButton1Visible) {
                    largeButton1.setBackgroundColor(Color.TRANSPARENT) // Invisible
                } else {
                    largeButton1.setBackgroundColor(getColor(R.color.buttonColor)) // Visible
                }
                isButton1Visible = !isButton1Visible

                // Repeat with the same delay
                handler.postDelayed(this, flickerRate10Hz)
            }
        }, flickerRate10Hz)
    }

    // Flicker button 2 at 15Hz
    private fun startFlicker15Hz() {
        handler.postDelayed(object : Runnable {
            override fun run() {
                // Toggle button visibility or background color
                if (isButton2Visible) {
                    largeButton2.setBackgroundColor(Color.TRANSPARENT) // Invisible
                } else {
                    largeButton2.setBackgroundColor(getColor(R.color.buttonColor)) // Visible
                }
                isButton2Visible = !isButton2Visible

                // Repeat with the same delay
                handler.postDelayed(this, flickerRate15Hz)
            }
        }, flickerRate15Hz)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Remove callbacks to stop flickering when the activity is destroyed
        handler.removeCallbacksAndMessages(null)

        // Unbind the service if bound
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }
}
