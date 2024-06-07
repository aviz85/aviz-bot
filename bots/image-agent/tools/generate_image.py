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
        "fofr/juggernaut-xl-lightning:c9a24c321ceb0b7843b872dcae82109dddadd1f82e94b115ee39289e0e182e40",
        input=input
    )

    # Get the URL of the generated image
    image_url = output[0]

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        # Create the uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), '../uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        # Define the path to save the image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = os.path.join(uploads_dir, f"generated_image_{timestamp}.png")

        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)

        return image_path
    else:
        raise ValueError(f"Failed to download image: {response.status_code}")

if __name__ == "__main__":
    # Example usage
    prompt = "A portrait photo, neon red hair, lightning storm"
    image_path = generate_image(prompt)
    print(f"Image saved at: {image_path}")
