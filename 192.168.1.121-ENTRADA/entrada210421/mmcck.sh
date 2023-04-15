echo "Downloading The Software for the Monk Makes Clever Card Kit"
echo "MAKE SURE YOU ARE CONNECTED TO THE INTERNET"
cd /home/pi
sudo apt-get install python-dev
git clone https://github.com/simonmonk/SPI-Py.git
cd SPI-Py
sudo python setup.py install
sudo python3 setup.py install
cd /home/pi
git clone https://github.com/simonmonk/squid.git
cd squid
sudo python setup.py install
sudo python3 setup.py install
sudo apt-get install alsa-utils
sudo apt-get install festival
sudo pip3 install guizero
cd /home/pi
git clone https://github.com/simonmonk/clever_card_kit.git
echo "Finished Installation"
echo "Please REBOOT using: $ sudo reboot"
