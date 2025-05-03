#!/bin/bash

# Define paths for the scripts
USBTransferScript="/path to your folder/StableDiffusion/usbtr.py"
DisplayScript="/path to your folder/StableDiffusion/display.py"
StableDiffusionScript="/path to your folder/StableDiffusion/sdlcd.py"

python $USBTransferScript

# Run display.py once
python $DisplayScript

# Infinite loop to run sdlcd.py repeatedly
while true
do
    python $StableDiffusionScript

    # Wait for five minutes before the next iteration
    sleep 300
done
