import asyncio
from random import randint
from PIL import Image
import requests
import os
import time
from time import sleep
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_generation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define the absolute paths
BASE_DIR = r"C:\Users\Dell\Downloads\AI\jarvis"
IMAGE_DATA_PATH = os.path.join(BASE_DIR, r"Frontend\Files\ImageGeneration.data")
STATUS_DATA_PATH = os.path.join(BASE_DIR, r"Frontend\Files\Status.data")
DATA_DIR = os.path.join(BASE_DIR, "Data")

# Function to update status
def update_status(message):
    logger.info(f"Status: {message}")
    try:
        with open(STATUS_DATA_PATH, "w") as f:
            f.write(message)
    except Exception as e:
        logger.error(f"Failed to update status: {e}")

# Function to check if the API key exists
def get_api_key():
    env_path = os.path.join(BASE_DIR, '.env')
    try:
        # First try using dotenv
        try:
            from dotenv import load_dotenv, get_key
            load_dotenv(env_path)
            api_key = get_key(env_path, 'HuggingFaceAPIKey')
            if api_key:
                return api_key
        except Exception as e:
            logger.warning(f"dotenv method failed: {e}")
            
        # Fallback to manual parsing
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('HuggingFaceAPIKey='):
                        return line.strip().split('=', 1)[1].strip('"\'')
        
        logger.error("API key not found in .env file")
        return None
    except Exception as e:
        logger.error(f"Error getting API key: {e}")
        return None

# Function to open and display images based on a given prompt
def open_images(prompt):
    # Ensure the Data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    prompt = prompt.replace(" ", "_")
    
    # Generate the filenames for the images
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]  # Changed to 4 images to match generation
    successfully_opened = 0
    
    for jpg_file in files:
        image_path = os.path.join(DATA_DIR, jpg_file)
        
        try:
            # Try to open and display the image
            if os.path.exists(image_path):
                logger.info(f"Opening Image: {image_path}")
                # Use Windows system command to open image
                os.system(f'start "" "{image_path}"')
                successfully_opened += 1
                sleep(1)
            else:
                logger.warning(f"Image file does not exist at {image_path}")
        except Exception as e:
            logger.error(f"Error opening {image_path}: {e}")
    
    return successfully_opened > 0

# API details for the Hugging Face stable diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"  # Changed to a more reliable model

# Async function to send a query to the Hugging Face API
async def query(payload, headers):
    try:
        logger.info(f"Sending API request with payload: {payload}")
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            # logger.info("API request successful")
            return response.content
        else:
            logger.error(f"API error: Status code {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error during API request: {e}")
        return None

# Async function to generate images based on the given prompt
async def generate_images(prompt: str, api_key: str):
    # Update status
    update_status("Generating images...")
    
    # Ensure the Data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not api_key:
        update_status("Error: API key not found")
        return False
    
    headers = {"Authorization": f"Bearer {api_key}"}
    tasks = []
    
    # Create 4 image generation tasks
    for i in range(4):
        seed = randint(0, 100000)
        payload = {
            "inputs": f"{prompt}, quality = 4K, sharpness=maximum, Ultra High details, high resolution",
            "parameters": {
                "seed": seed
            }
        }
        task = asyncio.create_task(query(payload, headers))
        tasks.append(task)
        
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Save the generated images to files
    successful_saves = 0
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                safe_prompt = prompt.replace(' ', '_').replace('/', '_').replace('\\', '_')
                file_path = os.path.join(DATA_DIR, f"{safe_prompt}{i+1}.jpg")
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                    successful_saves += 1
                    logger.info(f"Saved image {i+1} to {file_path}")
            except Exception as e:
                logger.error(f"Error saving image {i+1}: {e}")
    
    # Update status
    if successful_saves > 0:
        update_status(f"Generated {successful_saves} images successfully")
        return True
    else:
        update_status("Failed to generate any images")
        return False

def generate_and_open_images(prompt: str):
    """Improved wrapper function that handles errors better"""
    if not prompt or len(prompt.strip()) < 3:
        print("Error: Image prompt too short")
        return False
        
    # Log the request
    print(f"Image generation requested for prompt: '{prompt}'")
    
    # Get API key with better error handling
    api_key = get_api_key()
    if not api_key:
        print("Error: No API key found for image generation")
        update_status("Error: API key not found")
        return False
    
    try:
        # Write the prompt to the data file
        os.makedirs(os.path.dirname(IMAGE_DATA_PATH), exist_ok=True)
        with open(IMAGE_DATA_PATH, "w") as f:
            f.write(f"{prompt},True")
        
        # Update status
        update_status(f"Generating image for: {prompt}")
        
        # Set a timeout for the operation
        start_time = time.time()
        timeout = 60  # 60 seconds timeout
        
        # Start async image generation
        success = asyncio.run(generate_images(prompt, api_key))
        
        if success:
            # Wait a moment for files to be fully written
            time.sleep(1)
            
            # Try to open the images
            safe_prompt = prompt.replace(' ', '_').replace('/', '_').replace('\\', '_')
            
            # Check if images were actually generated
            expected_images = [os.path.join(DATA_DIR, f"{safe_prompt}{i+1}.jpg") for i in range(4)]
            images_exist = [os.path.exists(img) for img in expected_images]
            
            if any(images_exist):
                print(f"Opening {sum(images_exist)} generated images")
                open_images(prompt)
                return True
            else:
                print("Image generation reported success but no images found")
                return False
        else:
            print("Image generation failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in generate_and_open_images: {e}")
        update_status(f"Error: {str(e)}")
        
        # Try to reset the status
        try:
            with open(IMAGE_DATA_PATH, "w") as f:
                f.write("False,False")
        except Exception:
            pass
            
        return False
# Main loop to monitor for image generation requests
def main():
    logger.info("Image generation service started...")
    update_status("Ready")
    
    while True:
        try:
            # Ensure directories exist
            os.makedirs(os.path.dirname(IMAGE_DATA_PATH), exist_ok=True)
            os.makedirs(os.path.dirname(STATUS_DATA_PATH), exist_ok=True)
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # Read the status and prompt from the data file
            if not os.path.exists(IMAGE_DATA_PATH):
                with open(IMAGE_DATA_PATH, "w") as f:
                    f.write("False,False")
                sleep(2)
                continue
                
            try:
                with open(IMAGE_DATA_PATH, "r") as f:
                    data = f.read().strip()
            except Exception as e:
                logger.error(f"Error reading ImageGeneration.data: {e}")
                sleep(2)
                continue
                
            if not data or ',' not in data:
                sleep(2)
                continue
                
            try:
                parts = data.split(",", 1)
                if len(parts) < 2:
                    sleep(2)
                    continue
                    
                prompt, status = parts
                
                # If status indicates an image generation request
                if status.lower() == "true" and prompt and prompt.lower() != "false":
                    logger.info(f"Generating images for prompt: {prompt}")
                    update_status("Processing...")
                    
                    # Generate and open images
                    success = generate_and_open_images(prompt=prompt)
                    
                    # Reset the status in the file after generating images
                    with open(IMAGE_DATA_PATH, "w") as f:
                        f.write("False,False")
                    
                    if success:
                        update_status("Images generated successfully")
                    else:
                        update_status("Failed to generate images")
                    
                    logger.info("Image generation completed")
                else:
                    # Only log occasionally to prevent log spam
                    if randint(0, 10) == 0:
                        logger.debug("Waiting for image generation request")
                    sleep(2)
            except Exception as e:
                logger.error(f"Error processing data: {e}")
                sleep(2)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            try:
                update_status(f"Error: {str(e)}")
            except:
                pass
            sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Image generation service stopped by user")
        update_status("Stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        update_status(f"Fatal error: {str(e)}")