import numpy as np

# Example: Load and inspect data
data_13hz = np.load('13Hz_data.npy')
data_17hz = np.load('17Hz_data.npy')

print("13Hz data shape:", data_13hz.shape)
print("17Hz data shape:", data_17hz.shape)

# Inspecting some values
print("Sample values from 13Hz data:", data_13hz[:, :1, :])  # First 5 samples for each channel
print("Sample values from 17Hz data:", data_17hz[:, :1, :])  # First 5 samples for each channel
