import os
import time
import requests
from dotenv import load_dotenv

# Load the API token from the environment variable
load_dotenv()
LEONARDO_API_KEY = os.getenv('LEONARDO_API_KEY')
MODEL_ID = "b24e16ff-06e3-43eb-8d33-4416c2d75876"

if not LEONARDO_API_KEY:
    raise ValueError("Leonardo API token not found in environment variables")

def generate_image(prompt):
    print(f"Starting image generation with prompt: {prompt}")
    
    # Define the request payload
    payload = {
        "height": 1024,
        "prompt": prompt,
        "modelId": MODEL_ID,
        "width": 1024,
        "presetStyle": "CINEMATIC"
    }
    print(f"Request Payload: {payload}")

    # Send the request to create the image generation
    response = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/generations",
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {LEONARDO_API_KEY}",
            "content-type": "application/json"
        },
        json=payload
    )
    response_data = response.json()
    print(f"Generation response: {response_data}")

    if "sdGenerationJob" not in response_data or "generationId" not in response_data["sdGenerationJob"]:
        raise ValueError("Failed to initiate image generation")

    generation_id = response_data["sdGenerationJob"]["generationId"]
    print(f"Generation ID: {generation_id}")

    # Poll for the generation status
    while True:
        status_response = requests.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
            headers={
                "accept": "application/json",
                "authorization": f"Bearer {LEONARDO_API_KEY}"
            }
        )
        status_data = status_response.json()
        print(f"Status response: {status_data}")

        if "generations_by_pk" in status_data and "generated_images" in status_data["generations_by_pk"]:
            generated_images = status_data["generations_by_pk"]["generated_images"]
            if generated_images:
                # Return the URL of the first generated image
                image_url = generated_images[0]["url"]
                print(f"Image URL: {image_url}")
                return image_url

        time.sleep(2)  # Wait for 2 seconds before checking again

if __name__ == "__main__":
    # Example usage
    prompt = "A cat staring at a window"
    image_url = generate_image(prompt)
    print(f"Generated Image URL: {image_url}")
