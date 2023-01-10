
# piSaber
## A Raspberry Pi controlled lightsaber using neopixels
##


# Resources
https://fredrik.hubbe.net/lightsaber/v4/<BR>
https://www.thecustomsabershop.com/Pixel-Blades-C153.aspx<BR>
https://www.thecustomsabershop.com/1-Thick-walled-Trans-White-PolyC-40-long-P528.aspx<BR>
https://www.instructables.com/Arduino-Based-Lightsaber-With-Light-and-Sound-Effe/<BR>
    https://github.com/AlexGyver/EnglishProjects/tree/master/GyverSaber<BR>
PM8403/raspi demo https://www.youtube.com/watch?v=6YBBcBQpCiA<BR>

# hardware
### Neopixels
Since neopixels are 5V and raspi GPIO is 3.3V we need a 3.3V->5V signal converter (SN74AHCT125N)<BR>
Connect a 1000uF capacitor across 5V/GND to limit any spike in current draw by the neopixels.<BR>
A 330ohm resistor on the signal line to the neopixels.<BR>
NOTE: if you're powering the raspi and neopixels separately, be sure to connect the grounds together, otherwise the signal line gets corrupted.<BR>

### Moton sensor (MPU6050)
https://learn.adafruit.com/mpu6050-6-dof-accelerometer-and-gyro/pinouts<BR>



# sourcing blade
https://plasticworld.ca/product/acrylic-round-tube/ - $11 CAD clear acrylic - 6ft
https://www.thecustomsabershop.com/1-Thick-walled-Trans-White-PolyC-40-long-P528.aspx - $12 USD polyc (plus $40 shipping) 40"
https://www.professionalplastics.com/PolycarbTube - $97 USD 8ft polyC clear
http://k-mac-plastics.com/polycarbonate-tubes.htm - $4.45USD/ft polyC clear ($40 shipping)
https://www.homedepot.ca/product/metalux-residential-4ft-t8-bulb-tube-guard-with-end-caps/1001654143?rrec=true $8 CAD 4ft polyC clear

### going with PEX. very cheap and works really well
https://www.homedepot.ca/product/sharkbite-1-inch-x-10-feet-white-pex-pipe/1001013735

# install (from buster)
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip

sudo apt-get install git
https://github.com/settings/tokens
git config --global user.name ""
git config --global user.email ""
<commit a change and push it, fill in email/token>
git config --global credential.helper cache
    
sudo apt-get install samba samba-common-bin
sudo vi /etc/samba/smb.conf
[pi]
path = /home/pi/
writeable=Yes
create mask=0777
directory mask=0777
public=no
mangled names = no
sudo smbpasswd -a pi
sudo systemctl restart smbd

```

# install (for neopixels)
We'll be running neopixels using sudo - so must install module using sudo<BR>
https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage<BR>
```
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka
```

# install (for mpu6050)
https://www.electronicwings.com/raspberry-pi/raspberry-pi-i2c<BR>
Have to configure I2C on raspi using raspi-config<BR>
pip install asyncio
pip install smbus

