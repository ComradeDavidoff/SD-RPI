from diffusers import StableDiffusionPipeline
from PIL import Image
import time
import subprocess
import os
import random

def get_random_prompt(file_path):
    with open(file_path, "r") as file:
        prompts = file.readlines()
    return random.choice(prompts).strip()

def log_details(image_name, prompt, checkpoint):
    """Log image name, prompt, and checkpoint to output.log."""
    log_file = "output.log"
    with open(log_file, "a") as log:
        log.write(f"Image: {image_name}, Prompt: \"{prompt}\", Checkpoint: {checkpoint}\n")

def process_image():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_path = f"./images/{timestr}.png"
    name = f"{timestr}.png"

    # List all .safetensors files in the /models/ directory
    model_directory = "./models/"
    checkpoint_files = [f for f in os.listdir(model_directory) if f.endswith(".safetensors")]

    # Select a random .safetensors file
    selected_checkpoint = random.choice(checkpoint_files)
    print(f"Selected checkpoint: {selected_checkpoint}")

    # Get a random prompt from the prompts.txt file
    prompt_file_path = os.path.join(os.path.dirname(__file__), "prompts.txt")
    prompt = get_random_prompt(prompt_file_path)
    print(f"Selected prompt: {prompt}")

    # Initialize the pipeline with the selected checkpoint
    pipe = StableDiffusionPipeline.from_single_file(
        os.path.join(model_directory, selected_checkpoint),
        low_cpu_mem_usage=True
    )
    pipe = pipe.to("cpu")

    negative_prompt = "deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, very displeasing, bad ai-generated"
    image = pipe(prompt, negative_prompt=negative_prompt, num_inference_steps=36, width=800, height=480).images[0]

    # Save the generated image
    image.save(file_path)

    # Log details to output.log
    log_details(name, prompt, selected_checkpoint)

    # Display the image using fbi
    subprocess.run(f'sudo fbi -T 2 -d /dev/fb0 -noverbose -a {file_path}', shell=True)

process_image()
