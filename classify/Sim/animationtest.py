import numpy as np
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import paho.mqtt.client as mqtt
import json

# MQTT Broker details
MQTT_BROKER = "localhost"  # Change this to your broker address
MQTT_PORT = 1883
MQTT_TOPIC = "DAQ"

# Create MQTT client instance
client_id = 'sim'
client = mqtt.Client(client_id)

# Callback function to handle successful connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code: {rc}")
    client.subscribe(MQTT_TOPIC)  # Subscribe to a topic if needed

# Callback function to handle incoming messages
def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())

        frequency = message['frequency']
        
        eeg_data_list = message['eeg_data']
        eeg_data = np.array(eeg_data_list)

        print(f"Received EEG data for frequency {frequency}")
        print(f"EEG data shape: {eeg_data.shape}")
        print(f"EEG data shape: {eeg_data}")

    except Exception as e:
        print(f"Error processing message: {e}")


# Connect to the MQTT broker
def connect_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()  # Start the MQTT client loop in a separate thread

# Function to load data based on frequency selection
def load_data(frequency):
    try:
        if frequency == '13Hz':
            return np.load('Sim/13hz.npy')
        elif frequency == '17Hz':
            return np.load('Sim/17hz.npy')
        elif frequency == '21Hz':
            return np.load('Sim/21hz.npy')
        else:
            raise ValueError("Unknown frequency")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")
        return None

# Function to execute when animation is done
def on_animation_done():
    messagebox.showinfo("Animation Finished", "All frames of the animation have been completed!")


# function to load eeg_data
def send_eeg(eeg_data, frequency):    
    try:
        # Again load data if data is being send after normalization
        # eeg_data = load_data(frequency)
        print(eeg_data.shape)

        if eeg_data is None:
            return

        # Convert the EEG data to a JSON-serializable format (list of lists)
        eeg_data_list = eeg_data[:,:,:1].tolist()  # Convert the numpy array to a Python list

        # Create a message payload with the frequency and EEG data
        message = {
            'frequency': frequency,
            'eeg_data': eeg_data_list
        }

        # Convert the message to a JSON string
        message_json = json.dumps(message)

        # Publish data to the MQTT topic
        client.publish(MQTT_TOPIC, message_json)
        print(f"Sent EEG data for frequency {frequency} to MQTT broker")
    except Exception as e:
        print(f"Failed to send MQTT message: {e}")



# Function to initialize and run the animation
def start_animation(frequency):
    frequency_to_flag = {
        '13Hz': 0,
        '17Hz': 1,
        '21Hz': 2
    }

    eeg_data = load_data(frequency)

    send_eeg(eeg_data, frequency)

    # Get the corresponding flag value based on the frequency
    flag = frequency_to_flag.get(frequency)
    if flag is None:
        messagebox.showerror("Error", "Invalid frequency")
        return

    # Get the dimensions of the data
    n_samples, n_channels, n_trials = eeg_data.shape
    print(f"Data shape: {n_samples} samples, {n_channels} channels, {n_trials} trials")

    # Time vector (assuming the time axis is from 0 to n_samples-1)
    time = np.arange(n_samples)

    # Normalize the data for each channel
    eeg_data = eeg_data / np.max(np.abs(eeg_data), axis=0, keepdims=True)

    # Clear the previous figure and create a new one
    for widget in frame_graph.winfo_children():
        widget.destroy()

    # Create the new figure and axis for the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create a line object for each channel
    channel_labels = ['Oz', 'O1', 'O2', 'PO3', 'POz', 'PO7', 'PO8', 'PO4']  # Custom identifiers for each channel
    lines = [ax.plot([], [], label=channel_labels[i])[0] for i in range(n_channels)]

    # Set axis limits
    ax.set_xlim(0, n_samples-1)
    ax.set_ylim(-1.5, 3.0)
    ax.set_xlabel('Time (samples)')
    ax.set_ylabel('EEG Signal')

    # Move the legend outside the axis to the right
    ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5))

    # Initialize the function to clear previous data
    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    # Update function to animate the data
    def update(frame):
        print(f"Updating frame {frame}")

        # Update the plot for each channel
        for i, line in enumerate(lines):
            offset = i * 0.25
            line.set_data(time[:frame], eeg_data[:frame, i, 0] + offset)

        return lines

    # Create the animation
    ani = FuncAnimation(
        fig, 
        update, 
        frames=np.arange(1, n_samples+1, 5),  # Skipping frames for faster animation
        init_func=init, 
        interval=0.01, 
        blit=True,  # Efficient rendering
        repeat=False  # Stop after all frames are done
    )

    # Display the plot on the Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Adjust layout to avoid legend cut-off
    fig.tight_layout(pad=2.0)

# Function to initialize the empty plot
def initialize_empty_plot():
    # Create a new figure with empty data (just labels and axis)
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set axis limits
    ax.set_xlim(0, 100)  # Dummy time axis for an empty plot
    ax.set_ylim(-1.5, 3.0)  # Dummy y-axis limits
    ax.set_xlabel('Time (samples)')
    ax.set_ylabel('EEG Signal')

    # Display the empty plot on the Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to handle window close event
def on_window_close():
    print("Closing the application...")
    client.loop_stop()  # Stop the MQTT client loop
    root.quit()  # Close the Tkinter window

# Create the main Tkinter window
root = tk.Tk()
root.title("EEG Signal Sim")

# Frame for buttons and layout organization
frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)  # Align buttons vertically to the left

# Frame for the plot (graph)
frame_graph = tk.Frame(root)
frame_graph.pack(padx=10, pady=10)

# Create buttons for different frequency datasets with enhanced appearance
btn_13hz = tk.Button(frame_buttons, text="13Hz", command=lambda: start_animation('13Hz'),
                     width=15, height=3, font=('Arial', 14), bg='#4CAF50', fg='white', relief='raised')
btn_13hz.pack(side=tk.TOP, pady=10)

btn_17hz = tk.Button(frame_buttons, text="17Hz", command=lambda: start_animation('17Hz'),
                     width=15, height=3, font=('Arial', 14), bg='#2196F3', fg='white', relief='raised')
btn_17hz.pack(side=tk.TOP, pady=10)

btn_21hz = tk.Button(frame_buttons, text="21Hz", command=lambda: start_animation('21Hz'),
                     width=15, height=3, font=('Arial', 14), bg='#FF5722', fg='white', relief='raised')
btn_21hz.pack(side=tk.TOP, pady=10)

# Initialize the window with an empty graph
initialize_empty_plot()

# Connect to MQTT broker
connect_mqtt()

# Handle window close event
root.protocol("WM_DELETE_WINDOW", on_window_close)

# Run the Tkinter event loop
root.mainloop()
