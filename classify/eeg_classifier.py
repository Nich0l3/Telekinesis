!pip install mne

# Install required Python libraries for EEG processing and machine learning
!pip install numpy scipy matplotlib latexify-py skfeature-chappers

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib notebook
import os  # Built-in Python module, no need to install
import mne
import numpy as np
import matplotlib.pyplot as plt
import warnings

# Ignore warnings for a cleaner output
warnings.filterwarnings("ignore", message=".*annotation.*")

folder_path = r"C:\Users\qwerty\Desktop\SSVEP-based-EEG-signal-processing\Data"

def data_path(folder_path, data_format="gdf"):
    path_files = []  # Store paths of matching files
    files = []  # Store file names
    folders = []  # Store folder names

    # Walk through the directory and collect relevant files/folders
    for root, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(f".{data_format}"):
                full_path = os.path.join(root, filename)
                path_files.append(full_path)
                files.append(filename)
        folders.extend(dirnames)

    return path_files, files, folders

# Get the paths of all GDF files
path_files, files, folders = data_path(folder_path, data_format="gdf")

# Print the collected file paths
print("Found files:", files)
print("Full paths:", path_files)

# Ensure the path_files variable contains GDF file paths
print(f"Using GDF file: {path_files[0]}")

# Read the GDF file into a raw MNE object
raw = mne.io.read_raw_gdf(path_files[0], verbose=0)

# Extract the channel names from the raw data
channels_name = raw.ch_names

# Get the EEG data and transpose it to have channels as rows and samples as columns
data = 1e6 * raw.get_data().T  # Convert to microvolts if necessary

# Get the sampling frequency of the EEG data
fs = raw.info['sfreq']

# Extract labels from annotations
labels = raw.annotations.description

# Get the events and their corresponding indices
events, event_ind = mne.events_from_annotations(raw, verbose=0)

# Print all the relevant information
print(f"Data: {data.shape} \n")
print(f"Channels Name: {channels_name} \n")
print(f"Labels: {labels} \n")
print(f"Events: {events} \n")
print(f"Event Indices: {event_ind} \n")

"""Data Splitting"""

# Define the duration of each trial in seconds
time_trial = 5

# Initialize lists to store trial data for each label
data1, data2, data3 = [], [], []

# Define the labels for each stimulation frequency (as strings)
lab = ['33025', '33026', '33027']

# Create a list of the initialized data arrays to manage them easily
data_list = [data1, data2, data3]

# Loop through all GDF files in the given path
for i in range(len(path_files)):
    # Read the GDF file into an MNE raw object
    raw = mne.io.read_raw_gdf(path_files[i], verbose=0)

    # Get sampling frequency and channel names
    fs = raw.info['sfreq']
    channels_name = raw.ch_names

    # Calculate the number of samples per trial
    duration_trial = int(fs * time_trial)

    # Extract EEG data and transpose (channels as rows, samples as columns)
    data = 1e6 * raw.get_data().T  # Convert to microvolts if needed

    # Extract labels from annotations
    labels = np.array(raw.annotations.description)

    # Extract events and their start times
    events, _ = mne.events_from_annotations(raw, verbose=0)
    time_start_trial = events[:, 0]  # Start times of trials

    # Loop over the defined labels
    for j, val in enumerate(lab):
        # Find trials with the current label
        num_trials = np.where(labels == val)[0]

        # Initialize array to store data for this label
        data_trial = np.zeros((duration_trial, len(channels_name), len(num_trials)))

        # Extract data for each trial of the current label
        for ind, trial_index in enumerate(num_trials):
            start = time_start_trial[trial_index]
            data_trial[:, :, ind] = data[start:start + duration_trial, :]

        # Store the extracted trial data in the appropriate list
        data_list[j].append(data_trial)

# Concatenate all the data arrays along the third axis (trials)
data1 = np.concatenate(data1, axis=2)
data2 = np.concatenate(data2, axis=2)
data3 = np.concatenate(data3, axis=2)

# Print the shapes of the final concatenated data arrays
print(f"data1.shape: {data1.shape} \ndata2.shape: {data2.shape} \ndata3.shape: {data3.shape}")

"""Filtering/ feature Extraction / Preprocessing"""

#Import required libraries
import numpy as np
import mne
import warnings

# Import functions from the .py files in the Functions folder
from Filtering import filtering

# Step 4: Define your parameters for filtering
trial = 8            # Define trial number (trial 1 in Python index starts from 0)
order = 3            # Define filter order
f_low = 0.05         # Define lower cutoff frequency for the bandpass filter (Hz)
f_high = 100         # Define upper cutoff frequency for the bandpass filter (Hz)
notch_freq = 50      # Define frequency to be removed from the signal for notch filter (Hz)
quality_factor = 20  # Define quality factor for the notch filter
notch_filter = "on"  # on or off
filter_active = "on" # on or off
design_method = "IIR" # IIR or FIR
type_filter = "bandpass"  # low, high, bandpass, or bandstop
freq_stim = 13       # Define stimulation frequency

# Step 5: Apply bandpass filtering to the EEG data
filtered_data = filtering(data1, f_low, f_high, order, fs, notch_freq, quality_factor,
                          filter_active, notch_filter, type_filter, design_method)

# Print the shape of the filtered data to verify
print(f"Filtered data shape: {filtered_data.shape}")

"""CAR Filter (Common average reference)"""

#Import the CAR filter function
from Common_average_reference import car

# Step 3: Apply CAR filter to the data
# filtered_data shape: (1280, 8, 160)
data_car = car(filtered_data, reference_channel=None)  # Use all channels for average reference

# Step 4: Verify the shape of CAR-filtered data
print(f"CAR-filtered data shape: {data_car.shape}")

# Step 5: Extract the trial-specific data if needed
trial = 0  # Define trial number (0-indexed)
trial_data_car = data_car[:, :, trial]  # Extract data for the selected trial

# Step 6: Verify the trial data shape
print(f"CAR-filtered data for Trial {trial + 1}: {trial_data_car.shape}")

"""FFT (Fast Fourier Transform)"""

import numpy as np
from FFT import perform_fft, extract_signal
# Define parameters
trial = 0          # Trial number (1st trial = index 0)
channel = 6        # Channel number (7th channel = index 6)
fs = 256           # Sampling frequency (example value)

# Extract the signal for the given trial and channel
raw_signal, filtered_signal = extract_signal(data1, filtered_data, channel, trial)

# Perform FFT on the extracted signals
signal, filtered_signal, x_fft, x_filter_fft, f = perform_fft(raw_signal, filtered_signal, fs)

# Print the frequency components and their magnitudes
print("Frequencies:", f)
print("Raw FFT Magnitudes:", np.abs(x_fft))
print("Filtered FFT Magnitudes:", np.abs(x_filter_fft))

"""PSD (pre processing)"""

# Import your specific functions
from Filtering import filtering
from Common_average_reference import car
from PSDA import psda_analysis

# ----------------------------------- Step 1: Combine all datasets ----------------------------------------
# Assume data1, data2, data3 are already loaded as numpy arrays.
# Shape: (1280, 8, n_trials) for each dataset
data_total = np.concatenate((data1, data2, data3), axis=2)

# Create labels for the trials (modify if needed)
labels = np.concatenate((np.full(data1.shape[-1], 0),
                         np.full(data2.shape[-1], 1),
                         np.full(data3.shape[-1], 2)))

# -------------------------------- Step 2: Filtering for all datasets -------------------------------------
order = 3                # Filter order
f_low = 0.05             # Lower cutoff frequency (Hz)
f_high = 100             # Upper cutoff frequency (Hz)
notch_freq = 50          # Notch filter frequency to remove (Hz)
quality_factor = 20      # Quality factor for the notch filter
notch_filter = "on"      # Enable or disable notch filter
filter_active = "off"    # Enable or disable bandpass filter
type_filter = "bandpass" # Filter type: bandpass

# Apply filtering to the combined data
filtered_data = filtering(data_total, f_low, f_high, order, fs,
                          notch_freq, quality_factor, filter_active,
                          notch_filter, type_filter)

print(f"Filtered Data Shape: {filtered_data.shape}")

# ------------------------------------- Step 3: CAR Filtering --------------------------------------
# Apply Common Average Reference (CAR) filter
data_car = car(filtered_data)
print(f"CAR-Filtered Data Shape: {data_car.shape}")

# ---------------------------------- Step 4: PSDA Analysis ----------------------------------------
num_channel = [0, 1, 2]  # Select channels for analysis
num_harmonic = 2         # Number of harmonics per frequency
num_sample_neigh = 30    # Neighborhood samples for each frequency
f_stim = [13, 21, 17]    # Frequencies of stimulation (Hz)

# Perform PSDA analysis on the CAR-filtered data
predict_label = psda_analysis(data_car[:, num_channel], f_stim,
                              num_sample_neigh, fs, num_harmonic)

# Calculate and display accuracy
accuracy = np.sum(labels == predict_label) / len(predict_label) * 100
print(f"Accuracy: {accuracy:.2f}%")

"""CCA"""

# Import functions
from Filtering import filtering
from Common_average_reference import car
from CCA import cca

# ------------------------------------ Step 2: Load and Combine Data ----------------------------------------
# Assuming data1, data2, and data3 are already loaded
data_total = np.concatenate((data1, data2, data3), axis=2)

# Generate labels for each dataset (0, 1, 2)
labels = np.concatenate((np.full(data1.shape[-1], 0),
                         np.full(data2.shape[-1], 1),
                         np.full(data3.shape[-1], 2)))

# ------------------------------------ Step 3: Filter the Data ----------------------------------------
order = 4
f_low = 0.05
f_high = 100
notch_freq = 50
quality_factor = 20
notch_filter = "on"
filter_active = "off"
type_filter = "bandpass"

filtered_data = filtering(data_total, f_low, f_high, order, fs,
                          notch_freq, quality_factor, filter_active,
                          notch_filter, type_filter)

print(f"Filtered Data Shape: {filtered_data.shape}")

# ----------------------------------- Step 4: Apply CAR Filter ----------------------------------------
data_car = car(filtered_data)
print(f"CAR-Filtered Data Shape: {data_car.shape}")

# ----------------------------------- Step 5: Perform CCA Classification ----------------------------------------
num_channel = [0, 1, 2]   # List of channels to use
num_harmonic = 4          # Number of harmonics
f_stim = [13, 21, 17]     # Frequencies used for stimulation

# Use your CCA function to classify the EEG signals
predict_label = cca(data_car, fs, f_stim, num_channel, num_harmonic)

# ------------------------------------ Step 6: Calculate Accuracy ----------------------------------------
accuracy = np.sum(labels == predict_label) / len(predict_label) * 100
print(f"Classification Accuracy: {accuracy:.2f}%")

"""FoCCA"""

# Import the necessary modules
from Filtering import filtering
from Common_average_reference import car
from FoCCA import focca_analysis  # Import the FoCCA method

# Combine datasets along the third axis and create corresponding labels
data_total = np.concatenate((data1, data2, data3), axis=2)
labels = np.concatenate((np.full(data1.shape[-1], 0),
                         np.full(data2.shape[-1], 1),
                         np.full(data3.shape[-1], 2)))

print(f"Combined Data Shape: {data_total.shape}")
print(f"Labels Shape: {labels.shape}")

# -------------------------- Step 3: Apply Filtering -----------------------------------------
order = 4                # Filter order
f_low = 0.05             # Lower cutoff frequency (Hz)
f_high = 100             # Upper cutoff frequency (Hz)
notch_freq = 50          # Notch frequency to remove (Hz)
quality_factor = 20      # Quality factor for the notch filter
notch_filter = "on"      # Notch filter enabled
filter_active = "off"    # Bandpass filter disabled
type_filter = "bandpass" # Type of filter

# Apply the filtering
fs = 256
filtered_data = filtering(data_total, f_low, f_high, order, fs,
                          notch_freq, quality_factor, filter_active,
                          notch_filter, type_filter)

print(f"Filtered Data Shape: {filtered_data.shape}")

# -------------------------- Step 4: Apply CAR Filtering -------------------------------------
# Apply Common Average Referencing
data_car = car(filtered_data)
print(f"CAR-Filtered Data Shape: {data_car.shape}")

# ---------------------------- Step 5: FoCCA Analysis ---------------------------------------
num_harmonic = 2          # Number of harmonics for each frequency
f_stim = [13, 21, 17]     # Stimulation frequencies
num_channel = [0, 1, 2]   # Channels to analyze

# Parameters for FoCCA
a = [0.01, 0.1, 0, 3, 5]
b = [0.01, 0.1, 0, 1, 10]

# Perform FoCCA analysis and compute accuracy
accuracy = focca_analysis(data_car, labels, fs, f_stim, num_channel,
                          num_harmonic, a, b)

# Print the accuracy for each combination of 'a' and 'b'
print(f"FoCCA Accuracy Results: {accuracy}")

"""FBCCA"""

#Import functions from the files
import FBCCA
import Filtering
import Common_average_reference

# Combine all datasets
data_total = np.concatenate((data1, data2, data3), axis=2)
labels = np.concatenate((np.full(data1.shape[-1], 0),
                         np.full(data2.shape[-1], 1),
                         np.full(data3.shape[-1], 2)))

# Step 8: Define filtering parameters
order = 4                # Define filter order
f_low = 0.05             # Define lower cutoff frequency for the bandpass filter (Hz)
f_high = 100             # Define upper cutoff frequency for the bandpass filter (Hz)
notch_freq = 50          # Define frequency to be removed from the signal for notch filter (Hz)
quality_factor = 20      # Define quality factor for the notch filter
notch_filter = "on"      # on or off
filter_active = "off"    # on or off
type_filter = "bandpass" # low, high, bandpass, or bandstop

# Step 9: Apply notch filter to the EEG data
filtered_data = Filtering.filtering(data_total, f_low, f_high, order, fs,
                                     notch_freq, quality_factor,
                                     filter_active, notch_filter, type_filter)

# Step 10: Perform Common Average Reference (CAR)
data_car = Common_average_reference.car(filtered_data)

# Step 11: Define FBCCA parameters
method = 'm3'             # Type filter banks: M1, M2, M3
num_harmonic = 2          # Number of harmonics for each frequency stimulation
notch_filter = "off"      # on or off
filter_active = "on"      # on or off
type_filter = "bandpass"  # low, high, bandpass, or bandstop
f_stim = [13, 21, 17]     # Frequencies stimulation
num_channel = [0, 1]      # Number of Channels
a = [0.01, 0]
b = [0.001, 0]
filter_banks = [[10, 20, 30, 40, 50, 60, 70, 80, 90],
                [100, 100, 100, 100, 100, 100, 100, 100, 100]]

# Step 12: Perform FBCCA analysis
accuracy = FBCCA.fbcca_analysis(data_car, labels, fs, f_stim, num_channel,
                                 num_harmonic, a, b, filter_banks, order,
                                 notch_freq, quality_factor, filter_active,
                                 notch_filter, type_filter)

# Step 13: Print the accuracy results
print("Accuracy Results: ", accuracy)

"""FFT for feature extraction(The fft_feature_extraction function computes the FFT of the signal for the selected channels and extracts the power spectral density (PSD) for specified frequency subbands.)"""

#Import required modules from your project
import numpy as np
from Filtering import filtering
from Common_average_reference import car
from FFT_Feature_Extraction import fft_feature_extraction

#Combine datasets
data_total = np.concatenate((data1, data2, data3), axis=2)  # Combine along trial axis
labels = np.concatenate((
    np.full(data1.shape[-1], 0),  # Label 0 for data1
    np.full(data2.shape[-1], 1),  # Label 1 for data2
    np.full(data3.shape[-1], 2)   # Label 2 for data3
))
print(f"Combined Data Shape: {data_total.shape}")

# Apply Filtering
order = 3
notch_freq = 50
quality_factor = 20
subbands = [[12, 16, 20], [14, 18, 22]]
f_low = np.min(subbands) - 1
f_high = np.max(subbands) + 1
notch_filter = "on"
filter_active = "on"
type_filter = "bandpass"

filtered_data = filtering(
    data_total, f_low, f_high, order, fs, notch_freq,
    quality_factor, filter_active, notch_filter, type_filter
)
print(f"Filtered Data Shape: {filtered_data.shape}")

# Apply CAR
data_car = car(filtered_data)
print(f"CAR-Filtered Data Shape: {data_car.shape}")

# Perform FFT-Based Feature Extraction
num_channel = [0, 1]  # Select channels to analyze
features = fft_feature_extraction(data_car, fs, num_channel, subbands)

# Print the shape of the extracted features
print(f"Extracted Features Shape: {features.shape}")

"""Feature Extraction using CCA"""

#Import functions from the files
import Filtering
import Common_average_reference
import CCA_Feature_Extraction
import numpy as np

#Combine all datasets
data_total = np.concatenate((data1, data2, data3), axis=2)
labels = np.concatenate((np.full(data1.shape[-1], 0),
                         np.full(data2.shape[-1], 1),
                         np.full(data3.shape[-1], 2)))

# Define filtering parameters
order = 3                # Define filter order
notch_freq = 50          # Define frequency to be removed from the signal for notch filter (Hz)
quality_factor = 20      # Define quality factor for the notch filter
subbands = [[12, 16, 20], [14, 18, 22]]
f_low = np.min(subbands) - 1  # Define lower cutoff frequency for the bandpass filter (Hz)
f_high = np.max(subbands) + 1  # Define upper cutoff frequency for the bandpass filter (Hz)
notch_filter = "on"       # on or off
filter_active = "on"      # on or off
type_filter = "bandpass"  # low, high, bandpass, or bandstop

# Apply notch filter to the EEG data
filtered_data = Filtering.filtering(data_total, f_low, f_high, order, fs,
                                     notch_freq, quality_factor,
                                     filter_active, notch_filter, type_filter)

# Perform Common Average Reference (CAR)
data_car = Common_average_reference.car(filtered_data)

# Define parameters for feature extraction
num_harmonic = 2          # Number of harmonics for each frequency stimulation
f_stim = [13, 21, 17]     # Frequencies stimulation
num_channel = [0, 1]      # Number of Channels
title = f"Feature Extraction using CCA"

# Perform CCA feature extraction
features_extraction = CCA_Feature_Extraction.cca_feature_extraction(data_car, fs, f_stim, num_channel, num_harmonic)

# Print or visualize the extracted features
print("Extracted Features: ", features_extraction)

"""Feature Selection"""

# Import the feature selection function from the uploaded file
from Feature_selections import feature_selecions

# Define parameters for feature selection
num_features = 4
n_neighbors_MI = 5                 # Number of neighbors to consider for mutual information calculation.
L1_Parameter = 0.1                 # Parameter value for L1 regularization.
threshold_var = 0.001              # The threshold used for variance thresholding.
type_feature_selection = "anova"    # Options: var, anova, mi, ufs, rfe, rf, l1fs, tfs, fs, ffs, bfs
title = f"Feature selection using {type_feature_selection}"

# Perform feature selection
features = feature_selecions(features_extraction, labels, num_features, threshold_var,
                              n_neighbors_MI, L1_Parameter, type_feature_selection)

# Display the selected features
print(f"Selected features shape: {features.shape}")

"""Festure_extraction and Label values"""

import numpy as np
from Filtering import filtering
from Common_average_reference import car
from FFT_Feature_Extraction import fft_feature_extraction

fs = 256  # Sampling frequency

# Step 1: Combine all datasets along the trial axis
data_total = np.concatenate((data1, data2, data3), axis=2)  # (9, 1280, 160)
print(f"Combined Data Shape: {data_total.shape}")

# Step 2: Generate labels for each trial
labels = np.concatenate((
    np.full(data1.shape[-1], 0),  # Label 0 for 13 Hz stimulation (50 trials)
    np.full(data2.shape[-1], 1),  # Label 1 for 21 Hz stimulation (60 trials)
    np.full(data3.shape[-1], 2)   # Label 2 for 17 Hz stimulation (50 trials)
))
print(f"Labels Shape: {labels.shape}")
print(f"Labels: {np.unique(labels, return_counts=True)}")  # Check distribution

# Step 3: Apply Filtering
order = 3
notch_freq = 50
quality_factor = 20
subbands = [[12, 16, 20], [14, 18, 22]]
f_low = np.min(subbands) - 1  # 11 Hz
f_high = np.max(subbands) + 1  # 23 Hz
notch_filter = "on"
filter_active = "on"
type_filter = "bandpass"

filtered_data = filtering(
    data_total, f_low, f_high, order, fs, notch_freq,
    quality_factor, filter_active, notch_filter, type_filter
)
print(f"Filtered Data Shape: {filtered_data.shape}")

# Step 4: Apply Common Average Referencing (CAR)
data_car = car(filtered_data)
print(f"CAR-Filtered Data Shape: {data_car.shape}")

# Step 5: Perform FFT-Based Feature Extraction
num_channel = [0, 1]  # Example: Analyze first two channels
features_extraction = fft_feature_extraction(data_car, fs, num_channel, subbands)

print(f"Extracted Features Shape: {features_extraction.shape}")

# Step 6: Store Features and Labels for Classification
np.save("features_extraction.npy", features_extraction)
np.save("labels.npy", labels)

print("Features and labels saved successfully!")

"""Classification Models"""

# Step 1: Import necessary libraries
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Assuming `features_extraction` and `labels` are already available from the previous steps

# Step 2: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    features_extraction, labels, test_size=0.2, random_state=42
)

# Step 3: Standardize the features (important for models like SVM)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Step 4: Train classifiers (Logistic Regression, SVM, and Random Forest)

# Logistic Regression
logreg = LogisticRegression(max_iter=1000, random_state=42)
logreg.fit(X_train, y_train)

# Support Vector Machine
svm_model = SVC(kernel='linear', probability=True, random_state=42)
svm_model.fit(X_train, y_train)

# Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Step 5: Evaluate models on the test set
models = {"Logistic Regression": logreg, "SVM": svm_model, "Random Forest": rf_model}

for name, model in models.items():
    y_pred = model.predict(X_test)
    print(f"--- {name} ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(classification_report(y_test, y_pred))

# Step 6: Define action mapping based on predictions
def action_mapping(prediction):
    actions = {
        0: "Hand Movement (13Hz)",
        1: "Leg Movement (21Hz)",
        2: "Resting State (17Hz)"
    }
    return actions.get(prediction, "Unknown Action")

# Step 7: Test the model with some example data
sample = X_test[0].reshape(1, -1)  # Example data point
predicted_label = rf_model.predict(sample)[0]
predicted_action = action_mapping(predicted_label)

print(f"Predicted Action: {predicted_action}")



