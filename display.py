from PIL import Image
import subprocess
import os

def get_latest_image(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    latest_file = max(files, key=os.path.getctime)
    return latest_file

# Get the latest image in the /images folder
latest_image = get_latest_image("./images")

# Run a single subprocess before the loop using the latest image
subprocess.run(f'sudo fbi -T 2 -d /dev/fb0 -noverbose -a {latest_image}', shell=True)
