import os
from datetime import datetime
import requests
from openai import OpenAI

# Load the API key from the environment variable
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check if the API key is loaded
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")
    
# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define the function to generate the image
def generate_image(prompt, model="dall-e-3", n=1, size="1024x1024"):
    # Request the OpenAI API
    try:
        response = client.images.generate(
            prompt=prompt,
            n=n,
            size=size,
            model=model,
            response_format="url"
        )
    except Exception as e:
        raise ValueError(f"Error generating image: {str(e)}")

    # Get the URL of the generated image
    try:
        image_url = response.data[0].url
    except Exception as e:
        raise ValueError(f"Error parsing response: {str(e)}")

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        # Create the uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        # Define the path to save the image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        image_path = os.path.join(uploads_dir, filename)

        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)

        return image_path
    else:
        raise ValueError(f"Failed to download image: {response.status_code}")
