cdax-crypto-python
==================

Basic model/simulation of the C-DAX security functionalities.

Python dependencies:

* M2Crypto (OpenSSL Python binding)
* yaml (to read the configuration file)
  
To install on OSX for python version 2.7 install MacPorts and run:

```bash
sudo port install py27-yaml py27-m2crypto
```

On Debian Linux (or Ubuntu) use aptitude to install the dependencies:

```bash
sudo apt-get install python-m2crypto python-yaml
```

You can run the simulation by executing the main file:

```bash
python main.py
```
