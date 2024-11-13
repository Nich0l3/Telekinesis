# RASPBERRY PI ZERO 2 W         

## HEADLESS SETUP (AVOID USING THIS FOR NOW)

use setup.sh script for headless configuration
                                                                     
```
./setup.sh     
```

## SHELL ACCESS

### SSH via NETWORK


## RASPBERRY PI

install dependencies of linux and python 

```
dep/linux-dep.sh
python3 -m venv ~/.env
echo source ~/.env/bin/activate >> ~/.bash_aliases
source ~/.bashrc
pip install -r dep/python-dep
```                                                                                         
run the python script to test the broker (need multi-threading or something) 

```
python3 test.py
```
