import joblib
import numpy as np
from scipy.signal import butter, lfilter, iirnotch
from scipy.fftpack import fft
import os 

# Define filtering functions
def butter_bandpass(lowcut, highcut, fs, order=3):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data, axis=-1)
    return y

def apply_notch_filter(data, freq, fs, quality_factor):
    b, a = iirnotch(freq, quality_factor, fs)
    y = lfilter(b, a, data, axis=-1)
    return y

def car(data):
    avg_signal = np.mean(data, axis=1, keepdims=True)
    return data - avg_signal

def fft_feature_extraction(data, fs, channels, subbands):
    features = []
    for trial in range(data.shape[2]):  # Loop through trials
        trial_features = []
        for ch in channels:
            channel_data = data[ch, :, trial]
            N = len(channel_data)
            yf = fft(channel_data)
            xf = np.linspace(0.0, fs / 2.0, N // 2)
            band_features = []
            for band in subbands:
                idx_band = np.where((xf >= band[0]) & (xf <= band[1]))[0]
                band_power = np.sum(np.abs(yf[idx_band])**2)
                band_features.append(band_power)
            trial_features.extend(band_features)
        features.append(trial_features)
    return np.array(features)

# Load the scaler and SVM model
scaler = joblib.load('scaler.pkl')
svm_model = joblib.load('svm_model.pkl')

# Sampling frequency
fs = 256

# Preprocessing settings
order = 3
notch_freq = 50
quality_factor = 20
subbands = [[12, 16, 20], [14, 18, 22]]
f_low = np.min(subbands) - 1
f_high = np.max(subbands) + 1
filter_active = "on"
notch_filter = "on"

def process_and_predict(file_path, label):
    # Load data
    data = np.load(file_path)

    # Apply Filtering
    if filter_active == "on":
        filtered_data = apply_bandpass_filter(data, f_low, f_high, fs, order)
        if notch_filter == "on":
            filtered_data = apply_notch_filter(filtered_data, notch_freq, fs, quality_factor)
    else:
        filtered_data = data

    # Apply CAR
    data_car = car(filtered_data)

    # Feature extraction
    num_channel = [0, 1]
    features_extraction = fft_feature_extraction(data_car, fs, num_channel, subbands)

    # Print extracted features
    print("Extracted features for", label, "Hz:", features_extraction)

    # Standardize features
    standardized_features = scaler.transform(features_extraction)

    # Print standardized features
    print("Standardized features for", label, "Hz:", standardized_features)

    # Make predictions
    predictions = svm_model.predict(standardized_features)

    # Output predictions
    print(f"Predictions for {label} Hz data:", predictions)

    return predictions

###################################################################################

# File path to one of the training data files
file_path = 'data/17Hz_data.npy'  # Example for 13 Hz data
label = "17Hz"  # Label for this data

# Process and predict using the training data file
if os.path.exists(file_path):
    process_and_predict(file_path, label)
else:
    print(f"File {file_path} not found.")
