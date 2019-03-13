#!/bin/bash
# Main setup script to run on an empty Ubuntu server 16.04 server.
# Written by M. Haynes March 2019

clear
function pause(){
   read -p "$*"
}

echo "*****************************************************************************"
echo "*****************************************************************************"
echo "pop_climate"
echo ""
echo "    Copyright (C) 2019  MICHAEL HAYNES"
echo ""
echo "    This program is free software: you can redistribute it and/or modify"
echo "    it under the terms of the GNU General Public License as published by"
echo "    the Free Software Foundation, either version 3 of the License, or"
echo "    (at your option) any later version."
echo ""
echo "    This program is distributed in the hope that it will be useful,"
echo "    but WITHOUT ANY WARRANTY; without even the implied warranty of"
echo "    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
echo "    GNU General Public License for more details."
echo ""
echo "    You should have received a copy of the GNU General Public License"
echo "    along with this program.  If not, see <https://www.gnu.org/licenses/>."
echo "*****************************************************************************"
echo "*****************************************************************************"
echo ""
echo ""
pause "Press [Enter] to continue..."

echo "*****************************************************************************"
echo "running apt-get update/upgrade"
sudo apt-get update
sudo apt-get -y upgrade

echo "*****************************************************************************"
echo "running apt-get install"
sudo apt-get -y install python3-pip python3-venv unzip ffmpeg

#echo "*****************************************************************************"
#echo "Installing ImageMagick"  (To make an animated GIF and try that out)
#sudo apt -y install imagemagick-6.q16 

echo "*****************************************************************************"
echo "create directories"
mkdir -p /home/user/pop_climate/mths
mkdir /home/user/data

echo "*****************************************************************************"
echo "Setting up Virtual Python Environment:"
python3 -m venv ~/pop_climate/venv
source ~/pop_climate/venv/bin/activate
pip install --upgrade pip
pip install pandas rasterio matplotlib

echo "*****************************************************************************"
echo ""
echo "REBOOT!!  run sudo reboot"
echo ""
echo "Go to http://mbtaonbus and select a bus"

echo -n "Reboot? (y/n)?" && read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    sudo reboot
fi

#pop_climate
#
#    Copyright (C) 2019  MICHAEL HAYNES
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
