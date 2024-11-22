from Functions.Filtering import filtering
from Functions.Common_average_reference import car 
from Functions.CCA_Feature_Extraction import cca_feature_extraction
import paho.mqtt.client as mqtt
import numpy as np
import joblib
import time
import json

def count_values(arr):
    """
    Function to count occurrences of 0s, 1s, and 2s in a given array.
    
    Parameters:
    arr (list): The input array containing numbers.
    
    Returns:
    tuple: A tuple containing the count of 0s, 1s, and 2s in the array.
    """
    count_zeros = np.count_nonzero(arr == 0)
    count_ones = np.count_nonzero(arr == 1)
    count_twos = np.count_nonzero(arr == 2)
        
    return count_zeros, count_ones, count_twos

#########################       PRE PROCESSING      ##########################
order = 4
notch_freq = 50
quality_factor = 20
subbands = [[12, 16, 20], [14, 18, 22]]
f_low = np.min(subbands) - 1
f_high = np.max(subbands) + 1
notch_filter = "on"
filter_active = "on"
type_filter = "bandpass"
num_harmonic = 4
f_stim = [13, 21, 17]
num_channel = [0, 1]
window_size = 256  
overlap = 128      
fs = 256           

#############################     CCA     ####################################
num_harmonic = 4          # Number of harmonic for each frequency stimulation
f_stim = [13, 21, 17]     # Frequencies stimulation
num_channel = [0, 1]      # Number of Channel     

#########################     feature selection    ###########################
num_features = 24                  # pick any random high number it's result won't go beyond its limits :)
type_feature_selection = "anova"   # var, anova, mi, ufs, rfe, rf, l1fs, tfs, fs, ffs, bfs



###############################     FUNCTIONS       ##########################
def preprocess_data(raw_data):
    """
    Function to pre process data using bandpass filter, notch filter and CAR (remove noise and artifacts)
    
    Parameters:
    raw_data (np array): The input array contain raw eeg data from sim.
    
    Returns:
    data_car: A np array containing pre processed data.
    """
    filtered_data = filtering(raw_data, f_low, f_high, order, fs, notch_freq, quality_factor, 
                                    filter_active, notch_filter, type_filter)        
    data_car = car(filtered_data) 
    print('pre-processed data shape :', data_car.shape)
    return data_car

def extract_features(raw_data):
    features_extraction = cca_feature_extraction(raw_data, fs, f_stim, num_channel, num_harmonic)
    print('extracted features shape :', features_extraction.shape)
    return features_extraction

def normalize_inference(x_real_time, scaler_filename="normalize.joblib"):
    norm = joblib.load(scaler_filename)
    
    if x_real_time.ndim == 1:
        x_real_time = x_real_time.reshape(-1, 1)
    
    x_real_time_normalized = norm.transform(x_real_time)
    
    return x_real_time_normalized

def send_result(norm_features):
    feature_output = saved_model.predict(norm_features)
    z1,o1,t1 = count_values(feature_output)

    print(f"predicted result = {feature_output}")
    print(f"Result : Zeros: {z1}, Ones: {o1}, Twos: {t1}")
    mapping = { 0 : "0", 1 : "1" , 2 : "2"}
    print(mapping[ 0 if z1 > o1 and z1 > t1 else 1 if o1 > t1 else 2])

def on_message(client, userdata, msg):
    """
    This callback function processes the incoming MQTT message.
    It preprocesses the data, applies normalization, and performs classification.
    """
    try:
        message = json.loads(msg.payload.decode())
        eeg_data_list = message['eeg_data']
        eeg_data = np.array(eeg_data_list)

        pre_processed_data = preprocess_data(eeg_data)
        extracted_features = extract_features(pre_processed_data)
        features_normalization = normalize_inference(extracted_features)
        send_result(features_normalization)
 
    except Exception as e:
        print(f"Error processing message: {e}")

################################    CLASS           ############################



########################    import files   #####################################
# Load the pre-trained model and normalization pipeline
saved_model = joblib.load("trained_model.pkl")  
normalize = joblib.load("normalize.joblib") 


# MQTT Settings
MQTT_BROKER = "localhost"  
MQTT_TOPIC = "DAQ"        
MQTT_PORT = 1883


# Set up the MQTT client
client = mqtt.Client()

# Connect to the broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Subscribe to the relevant topic for real-time data
client.subscribe(MQTT_TOPIC)

# Attach the on_message callback function to handle incoming messages
client.on_message = on_message

# Loop to keep the client connected and listening for messages
print("Waiting for real-time data from MQTT...")
client.loop_start()

# Example: Keeping the program running for a while to receive MQTT messages (can be adjusted)
try:
    while True:
        time.sleep(1)  # Simulate waiting for incoming MQTT messages
except KeyboardInterrupt:
    print("Terminating MQTT client")
    client.loop_stop()
    client.disconnect()
