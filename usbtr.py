import os
import subprocess
import shutil
import time
from PIL import Image, ImageDraw, ImageFont

# Updated system paths
system_models_path = "./models"
system_images_path = "./images"
system_prompts_path = "./prompts.txt"
system_logs_path = "./output.log"

def display_status(message):
    """Generate and display a status image using FBI with manual line breaks."""
    image_path = "/tmp/status.png"
    width, height = 800, 480  # Adjust dimensions to match your screen
    img = Image.new("RGB", (width, height), color="black")
    draw = ImageDraw.Draw(img)

    # Add the message text with manual line breaks
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Example font
    font = ImageFont.truetype(font_path, size=40)

    # Split the message by line breaks for manual control
    lines = message.split('\n')
    line_height = 40  # Fixed height for each line based on font size
    total_height = line_height * len(lines)  # Total height of text block
    y_position = (height - total_height) // 2  # Center the text block vertically

    for line in lines:
        text_width = font.getbbox(line)[2]  # Calculate text width
        x_position = (width - text_width) // 2  # Center each line horizontally
        draw.text((x_position, y_position), line, fill="white", font=font)
        y_position += line_height  # Move to the next line position

    # Save the generated image
    img.save(image_path)

    # Display the image using fbi
    subprocess.run(f'sudo fbi -T 2 -d /dev/fb0 --noverbose -a {image_path}', shell=True)

    # Add a short delay for readability
    time.sleep(1)

def detect_and_mount_usb():
    """Detect and mount a USB device."""
    display_status("Scanning for USB...\nPlease wait")
    for device in os.listdir('/dev'):
        if device.startswith('sd') and device[-1].isdigit():  # Detects sda1, sdb1, etc.
            device_path = f"/dev/{device}"
            mount_point = '/media/usb_drive'

            # Ensure the directory exists with correct permissions
            subprocess.run(['sudo', 'mkdir', '-p', mount_point], check=True)
            subprocess.run(['sudo', 'chmod', '777', mount_point], check=True)

            # Attempt to mount the device
            result = subprocess.run(['sudo', 'mount', device_path, mount_point], stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                display_status(f"Mounted {device_path}\nat {mount_point}")
                return mount_point, device_path
            else:
                display_status(f"Failed to mount {device_path}")
                print(f"Error: {result.stderr}")

    display_status("No USB device detected.")
    return None, None

def transfer_and_cleanup(usb_images_path):
    """Transfer all files and delete everything except the latest image."""
    display_status("Transferring 'images'...\nPreparing cleanup.")
    if os.path.exists(system_images_path) and os.listdir(system_images_path):
        all_items = [os.path.join(system_images_path, f) for f in os.listdir(system_images_path)]
        files_only = [f for f in all_items if os.path.isfile(f)]
        if files_only:
            # Sort files by last modification time
            files_only.sort(key=os.path.getmtime, reverse=True)
            most_recent_file = files_only[0]

            # Transfer all files to the USB
            for item in files_only:
                shutil.copy(item, usb_images_path)

            # Delete all files except the most recent one
            for item in files_only:
                if item != most_recent_file:
                    os.remove(item)

            # Provide feedback
            display_status(f"Transfer complete.\nCleanup completed.\nLatest file retained:\n{os.path.basename(most_recent_file)}")
        else:
            display_status("'images' folder is empty.\nNothing to process.")
    else:
        display_status("'images' folder not found.\nSkipping operation.")

def handle_prompts(usb_mount_point):
    """Copy and transfer prompts.txt files as specified."""
    usb_prompts_path = os.path.join(usb_mount_point, "prompts.txt")
    current_time = time.strftime("%Y%m%d-%H%M%S")

    # Copy and rename local prompts.txt to USB
    display_status("Copying local prompts.txt\nto USB with timestamp.")
    if os.path.exists(system_prompts_path):
        renamed_file = f"prompts{current_time}.txt"
        shutil.copy(system_prompts_path, os.path.join(usb_mount_point, renamed_file))
        display_status(f"Copied and renamed to:\n{renamed_file}")
    else:
        display_status("No local prompts.txt found.\nSkipping copy.")

    # Overwrite local prompts.txt with USB prompts.txt if it exists
    display_status("Checking for prompts.txt\non USB to overwrite system.")
    if os.path.exists(usb_prompts_path):
        shutil.copy(usb_prompts_path, system_prompts_path)
        display_status("USB prompts.txt copied.\nSystem file overwritten.")
    else:
        display_status("No prompts.txt found on USB.\nSkipping overwrite.")

def handle_logs(usb_mount_point):
    """Copy and transfer prompts.txt files as specified."""
    usb_logs_path = os.path.join(usb_mount_point, "output.log")
    current_time = time.strftime("%Y%m%d-%H%M%S")

    # Copy and rename local output.log to USB
    display_status("Copying local output.log\nto USB with timestamp.")
    if os.path.exists(system_logs_path):
        renamed_file = f"output{current_time}.log"
        shutil.copy(system_logs_path, os.path.join(usb_mount_point, renamed_file))
        display_status(f"Copied and renamed to:\n{renamed_file}")
    else:
        display_status("No local output.log found.\nSkipping copy.")

def unmount_usb(device_path):
    """Unmount the USB device."""
    display_status("Unmounting USB...")
    result = subprocess.run(['sudo', 'umount', device_path], stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        display_status("USB unmounted successfully!")
    else:
        display_status(f"Failed to unmount USB:\n{device_path}")
        print(f"Error: {result.stderr}")

def transfer_files(usb_mount_point):
    """Handle the file transfer logic."""
    usb_models_path = os.path.join(usb_mount_point, "models")
    usb_images_path = os.path.join(usb_mount_point, "images")

    # Transfer 'models' from USB to system
    display_status("Transferring 'models'...")
    if os.path.exists(usb_models_path):
        # Correct destination folder
        if not os.path.exists(system_models_path):  # Ensure destination exists
            os.makedirs(system_models_path)
        for item in os.listdir(usb_models_path):
            source = os.path.join(usb_models_path, item)
            destination = os.path.join(system_models_path, item)  # No extra nesting
            if not os.path.exists(destination):  # Skip if the file already exists
                if os.path.isdir(source):
                    shutil.copytree(source, destination, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, destination)
        display_status("'models' Copied to system!")
    else:
        display_status("'models' Not Found on USB.\nSkipping transfer.")

    # Call function to transfer and clean up 'images'
    if os.path.exists(usb_images_path):
        transfer_and_cleanup(usb_images_path)
    else:
        display_status("'images' folder not found on USB.\nSkipping transfer.")

    # Handle prompts.txt files
    handle_prompts(usb_mount_point)

    # Handle output.log files
    handle_logs(usb_mount_point)

if __name__ == "__main__":
    usb_mount_point, device_path = detect_and_mount_usb()
    if usb_mount_point and device_path:
        transfer_files(usb_mount_point)
        unmount_usb(device_path)
    else:
#        display_status("USB Detection or\nMounting Failed.")
        display_status("No USB Detected")
