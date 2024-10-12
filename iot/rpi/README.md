# RASPBERRY PI ZERO 2 W         

## HEADLESS SETUP

use setup.sh script for headless configuration
                                                                     
```
./setup.sh     
```

## SHELL ACCESS

### SSH via NETWORK


## RASPBERRY PI

step 1 : run dep/linux-dep.sh script to install important dependencies and copy config files

```
dep/linux-dep.sh
```
                                                                 
step 2 :  make a python virtual environment and install dependencies
                                                                 
```
python3 -m venv ~/.env
echo source ~/.env/bin/activate >> ~/.bash_aliases
source ~/.bashrc
pip install -r dep/python-dep
```                           
                                                                 
step 3 : run the python script to tedt the broker (need multi-threading or something) 

```
python3 test.py
```
