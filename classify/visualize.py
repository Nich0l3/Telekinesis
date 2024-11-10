import matplotlib.pyplot as plt
import numpy as np
import os

# Load the data
output_dir = r'C:\Users\qwerty\Desktop\Telekinesis\classify\data'

# List of frequencies to plot
frequencies = [13, 17, 21]

# Font size settings
title_fontsize = 8
label_fontsize = 6
tick_fontsize = 8

# Set the number of epochs per plot
epochs_per_plot = 5  # Adjust this number based on your preference

# Loop through each frequency
for freq in frequencies:
    # Path to the .npy file for the specific frequency data
    file_path = os.path.join(output_dir, f'{freq}Hz_data.npy')

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist. Please check the path.")

    # Load the data
    try:
        data = np.load(file_path)
        print(f"Loaded data from {file_path}")
    except Exception as e:
        raise Exception(f"An error occurred while loading the .npy file: {e}")

    # Check the shape of the data
    print(f"{freq} Hz data shape: {data.shape}")

    # Number of channels and epochs
    num_channels = data.shape[1]
    num_epochs = data.shape[0]

    # Calculate the number of plots needed
    num_plots = (num_epochs + epochs_per_plot - 1) // epochs_per_plot  # Calculate the number of plots needed

    # Plot all epochs for all channels
    for plot_index in range(num_plots):
        plt.figure(figsize=(15, 10))

        # Plot the epochs for each channel in the current plot
        for channel in range(num_channels):
            for epoch in range(epochs_per_plot):
                epoch_index = plot_index * epochs_per_plot + epoch

                if epoch_index < num_epochs:  # Check to avoid out-of-bounds
                    ax = plt.subplot(num_channels, epochs_per_plot, channel * epochs_per_plot + epoch + 1)
                    ax.plot(data[epoch_index, channel, :])
                    ax.set_title(f'Ch {channel + 1}, Epoch {epoch_index + 1} at {freq} Hz', fontsize=title_fontsize)
                    ax.set_xlabel('Time Points', fontsize=label_fontsize)
                    ax.set_ylabel('EEG Signal Amplitude', fontsize=label_fontsize)
                    ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)  # Reduce tick font size

        plt.tight_layout()
        plt.suptitle(f'EEG Data at {freq} Hz', fontsize=12, y=1.02)  # Title for the entire plot
        plt.show()  # Show the plot for the current frequency
