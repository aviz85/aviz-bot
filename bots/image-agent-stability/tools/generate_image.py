import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load the API token from the environment variable
load_dotenv()
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')

# Define the function to generate the image
def generate_image(prompt):
    if not STABILITY_API_KEY:
        raise ValueError("Stability API key not found in environment variables")

    # Define the input for the model
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }
    data = {
        "prompt": prompt,
        "output_format": "png"
    }

    # Run the model
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/ultra",
        headers=headers,
        files={"none": ''},  # Required due to multipart/form-data
        data=data
    )

    # Check response status
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

        # Construct the relative URL
        relative_url = f"/uploads/{filename}"
        return relative_url
    else:
        raise ValueError(f"Failed to generate image: {response.status_code}")