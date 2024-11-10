import mne
file_path = r'C:\Users\qwerty\Desktop\SSVEP-based-EEG-signal-processing\Data\Subject2-[2012.04.07-19.27.02].gdf'
# Load the GDF file
raw = mne.io.read_raw_gdf(file_path, preload=True)

# Extract events
events, event_id = mne.events_from_annotations(raw)
print("Events found:", event_id)


# Define the frequencies corresponding to the labels
freq_map = {
   # '33024': 0,  # Resting class (no stimulation)
    '33025': 13,  # 13 Hz
    '33026': 21,  # 21 Hz
    '33027': 17   # 17 Hz
}

# Extract the epochs for each frequency
epochs = {}
for label, freq in freq_map.items():
        epochs[label] = mne.Epochs(raw, events, event_id={label: event_id[label]}, tmin=1.0, tmax=6.0, baseline=None, preload=True)
import numpy as np
import os

# Create a directory to save the data files
output_dir = r'C:\Users\qwerty\Desktop\Telekinesis\classify\data'
os.makedirs(output_dir, exist_ok=True)

def save_epochs_to_file(epochs, label, freq):
    data = epochs.get_data()  # Shape: (n_epochs, n_channels, n_times)
    file_path = os.path.join(output_dir, f'{freq}Hz_data.npy')
    np.save(file_path, data)
    print(f'Saved {freq} Hz data to {file_path}')

print(epochs)
with open("epochs.txt",'w') as file:  
    file.write(str(epochs))

# Save the data for each frequency
for label, freq in freq_map.items():
    if label in epochs:
        save_epochs_to_file(epochs[label], label, freq)
