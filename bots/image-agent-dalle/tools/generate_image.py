import os
from datetime import datetime
import requests
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the API key from the environment variable
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check if the API key is loaded
if OPENAI_API_KEY is None:
    logging.error("OPENAI_API_KEY not found in environment variables.")
    raise ValueError("OPENAI_API_KEY not found in environment variables.")
else:
    logging.debug("OPENAI_API_KEY loaded successfully.")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logging.debug("OpenAI client initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {str(e)}")
    raise

# Define the function to generate the image
def generate_image(prompt, model="dall-e-3", n=1, size="1024x1024"):
    logging.debug(f"Generating image with prompt: {prompt}, model: {model}, n: {n}, size: {size}")
    
    # Request the OpenAI API
    try:
        response = client.images.generate(
            prompt=prompt,
            n=n,
            size=size,
            model=model,
            response_format="url"
        )
        logging.debug("Image generated successfully from OpenAI API.")
    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        raise ValueError(f"Error generating image: {str(e)}")

    # Get the URL of the generated image
    try:
        image_url = response.data[0].url
        logging.debug(f"Generated image URL: {image_url}")
    except Exception as e:
        logging.error(f"Error parsing response: {str(e)}")
        raise ValueError(f"Error parsing response: {str(e)}")

    # Download the image
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            logging.debug("Image downloaded successfully.")
        else:
            logging.error(f"Failed to download image: {response.status_code}")
            raise ValueError(f"Failed to download image: {response.status_code}")
    except Exception as e:
        logging.error(f"Error downloading image: {str(e)}")
        raise

    # Create the uploads directory if it doesn't exist
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        logging.debug(f"Uploads directory: {uploads_dir}")
    except Exception as e:
        logging.error(f"Error creating uploads directory: {str(e)}")
        raise

    # Define the path to save the image
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        image_path = os.path.join(uploads_dir, filename)

        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)
            logging.debug(f"Image saved successfully at {image_path}")

        # Construct the relative URL
        relative_url = f"/uploads/{filename}"
        logging.debug(f"Relative URL of the image: {relative_url}")
        return relative_url
    except Exception as e:
        logging.error(f"Error saving image: {str(e)}")
        raise