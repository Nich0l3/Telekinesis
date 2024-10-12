#!/bin/bash

#####    ONLY CHANGE THESE VARIABLES (unless you know what you are doing) ######
DEVICE="/dev/sda"
MOUNT="/media/ubie"
BOOTFS="$MOUNT/bootfs"
CONFIG_FILE="$BOOTFS/wpa_supplicant.conf"
ENABLE_SSH=1 
OS_FILE="$HOME/Downloads/iso/2024-07-04-raspios-bookworm-arm64.img.xz"
NW_SETUP=1
################################################################################


initial_prompt(){
  echo before continuing check whether you have initialized these variables
  echo 1. MOUNT POINT : $MOUNT
  echo 2. ENABLE_SSH  : $ENABLE_SSH
  echo 3. OS_FILE     : $OS_FILE
  echo 4. DEVICE      : $DEVICE
  echo
  read -p "type exit to reoconfig and enter to continue : " CHOICE

  if [ "${CHOICE,,}" = "exit" ]; # this will convert CHOICE value to lowercase
  then 
    exit
  fi
}

install_os(){

  read -p "want to install a fresh image ? (y/N):" CHOICE

  if [ "${CHOICE,,}" = "y" ]; then
      if ! sudo dd if="$OS_FILE" of="$DEVICE" status=progress bs=4M; then
          echo "Error: Installation failed."
          return 1
      fi
      sync
      echo "Installation complete."
  else
      echo "Installation canceled."
  fi

}

display_networks(){
  echo $NW_SETUP
  read -p "want to config n/w (y/N) : " CHOICE

  if [ "${CHOICE,,}" = "y" ];then
    NW_SETUP=1
  	nmcli d w rescan
	  nmcli d w list
  else
    NW_SETUP=0
  fi
  echo $NW_SETUP
}

create_wpa_supplicant_conf() {
  
  echo $NW_SETUP
  if [ "$NW_SETUP" -ne 0 ]; then
   
    read -p "enter SSID : "      SSID
    read -sp "enter password : " PASSWORD
    echo

    if [ -z "$PASSWORD" ]; then
      echo "Password cannot be empty."
      return 1
    fi

    CONFIG=$(wpa_passphrase "$SSID" "$PASSWORD")

    # Create the wpa_supplicant.conf file
    cat <<EOL > $CONFIG_FILE
country=in
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

$CONFIG
EOL

    sed -i '/#psk/d' $CONFIG_FILE
    echo "wpa_supplicant.conf created at $CONFIG_FILE"

  fi
}

create_user_conf() {
  
  read -p "change user config? (necessary for initial setup don't know about other times) (y/N) : " CHOICE

  if [ "${CHOICE,,}" = "y" ];then
    read -p "enter username : "   USR
    read -sp "enter password : "  PASSWORD
    echo "$USR:$(echo $PASSWORD | openssl passwd -6 -stdin)" > $BOOTFS/userconf.txt
  fi
}

enable_ssh(){
  if $ENABLE_SSH; then
    touch $BOOTFS/ssh
  fi
}

###################################     MAIN    #########################################

initial_prompt 
install_os

echo network setup begin ...
display_networks 
create_wpa_supplicant_conf 
echo network setup complete ...
echo

echo user setup begin ...
create_user_conf
echo user config complete ...

enable_ssh 

