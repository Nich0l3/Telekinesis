import numpy as np
import os

# Path to the directory where .npy files are saved
output_dir = r'C:\Users\qwerty\Desktop\Telekinesis\classify\data'

# Load and inspect the 13 Hz data
file_path_13hz = os.path.join(output_dir, '13Hz_data.npy')
data_13hz = np.load(file_path_13hz)
print(f'13 Hz data shape: {data_13hz.shape}')
print(data_13hz)

# Load and inspect the 21 Hz data
file_path_21hz = os.path.join(output_dir, '21Hz_data.npy')
data_21hz = np.load(file_path_21hz)
print(f'21 Hz data shape: {data_21hz.shape}')
print(data_21hz)

# Load and inspect the 17 Hz data
file_path_17hz = os.path.join(output_dir, '17Hz_data.npy')
data_17hz = np.load(file_path_17hz)
print(f'17 Hz data shape: {data_17hz.shape}')
print(data_17hz)
