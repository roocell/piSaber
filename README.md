
# piSaber
## A Raspberry Pi controlled lightsaber using neopixels


# Resources
https://fredrik.hubbe.net/lightsaber/v4/
https://www.thecustomsabershop.com/Pixel-Blades-C153.aspx
https://www.thecustomsabershop.com/1-Thick-walled-Trans-White-PolyC-40-long-P528.aspx
https://www.instructables.com/Arduino-Based-Lightsaber-With-Light-and-Sound-Effe/
    https://github.com/AlexGyver/EnglishProjects/tree/master/GyverSaber
PM8403/raspi demo https://www.youtube.com/watch?v=6YBBcBQpCiA

# sourcing blade
https://plasticworld.ca/product/acrylic-round-tube/ - $11 CAD clear acrylic - 6ft
https://www.thecustomsabershop.com/1-Thick-walled-Trans-White-PolyC-40-long-P528.aspx - $12 USD polyc (plus $40 shipping) 40"
https://www.professionalplastics.com/PolycarbTube - $97 USD 8ft polyC clear
http://k-mac-plastics.com/polycarbonate-tubes.htm - $4.45USD/ft polyC clear ($40 shipping)
https://www.homedepot.ca/product/metalux-residential-4ft-t8-bulb-tube-guard-with-end-caps/1001654143?rrec=true $8 CAD 4ft polyC clear

### going with PEX. very cheap and works really well
https://www.homedepot.ca/product/sharkbite-1-inch-x-10-feet-white-pex-pipe/1001013735

# install (from buster)
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip

sudo apt-get install git
https://github.com/settings/tokens
git config --global user.name ""
git config --global user.email ""
<commit a change and push it, fill in email/token>
git config --global credential.helper cache

#
