#!/bin/bash

display_networks(){
	nmcli d w rescan
	nmcli d w list
}

# Function to create wpa_supplicant.conf
create_wpa_supplicant_conf() {
    SSID=$1
    PASSWORD=$2
    CONFIG_FILE="./wpa_supplicant.conf"

    # Create the wpa_supplicant.conf file
    cat <<EOL > $CONFIG_FILE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="$SSID"
    psk="$PASSWORD"
    key_mgmt=WPA-PSK
}
EOL

    echo "wpa_supplicant.conf created at $CONFIG_FILE"
}

# Check for root user
if [ "$EUID" -ne 0 ];then
	echo "Please run as a root user"
	exit 1
fi

# Display networks
display_networks

# Prompt for user input
read -p "Enter the SSID of the Wi-Fi: " SSID
read -sp "Enter the Password of the Wi-Fi: " PASSWORD
echo

# Call the function to create the config file
create_wpa_supplicant_conf "$SSID" "$PASSWORD"
