import os
import replicate
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load the API token from the environment variable
load_dotenv()
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

# Define the function to generate the image
def generate_image(prompt):
    if not REPLICATE_API_TOKEN:
        raise ValueError("Replicate API token not found in environment variables")

    # Define the input for the model
    input = {
        "prompt": prompt
    }

    # Run the model
    output = replicate.run(
        "bytedance/sdxl-lightning-4step:5f24084160c9089501c1b3545d9be3c27883ae2239b6f412990e82d4a6210f8f",
        input=input
    )

    # Get the URL of the generated image
    image_url = output[0]
    return image_url
    
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

        # Construct the relative URL
        relative_url = f"/uploads/{filename}"
        return relative_url
    else:
        raise ValueError(f"Failed to download image: {response.status_code}")

if __name__ == "__main__":
    # Example usage
    prompt = "A portrait photo, neon red hair, lightning storm"
    image_path = generate_image(prompt)
    print(f"Image saved at: {image_path}")
