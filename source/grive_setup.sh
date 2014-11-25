#!/bin/bash
echo "Downloading and Installing grive dependencies. One Mement Please ......."
sudo apt-get install libgcrypt11-dev libjson0-dev libcurl4-openssl-dev libexpat1-dev libboost-filesystem-dev libboost-program-options-dev libboost-all-dev libyajl-dev
echo "----------- grive Dependencies Installed --------------------"
echo "Steps to initialize grive"
echo "1  Open a web browser on your PC and login to google. eg gmail and open a new blank tab"
echo "2  Use putty ssh to login into the raspberry pi to be setup"
echo "3  Change to the required pi motion detection folder containing grive, pimotion.py and sync.sh"
echo "4  Run ./grive -a to initialize to setup grive"
echo "5  Highlight the very long URL returned by grive -a command"
echo "6  Move mouse to the browser window and right click paste into url box in browser"
echo "   and hit return to go to the web page"
echo "7  Hit accept button then copy security code (highlight then right click copy or type ctrl-c"
echo "8  Move mouse to putty session and paste (right click) at grive entry requesting code"
echo "9  grive will then authenticate and start to try to syncronize with the current folder."
echo "   Hit ctrl-c to stop"
echo "10 Copy .grive file into google_drive folder.  It should not be necessary to copy"
echo "   the .grive_state file if it exists but no harm if you don't"
echo "11 Start sudo ./pimotion.py and generate some motion images. "
echo "   A .sync file should be created. Ctrl-c to exit the python script"
echo "12 Manually execute sudo ./sync.sh to start a synchronization session"
echo "   and verify everything is working OK."
