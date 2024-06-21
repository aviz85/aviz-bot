import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

def generate_image(prompt):
    # Shutterstock API endpoint for image search
    url = "https://api.shutterstock.com/v2/images/search"
    
    # Get the API key from environment variable
    consumer_key = os.getenv("SHUTTERSTOCK_CONSUMER_KEY")
    consumer_secret = os.getenv("SHUTTERSTOCK_CONSUMER_SECRET")
    
    if not consumer_key or not consumer_secret:
        return "Error: Shutterstock API credentials not found in environment variables."
    
    # Basic authentication credentials
    credentials = (consumer_key, consumer_secret)
    
    # Parameters for the API request
    params = {
        "query": prompt,
    }
    
    try:
        # Make the API request
        response = requests.get(url, auth=credentials, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Check if photos are found
        if data["total_count"] > 0:
            # Return the URL of the first photo
            return data["data"][0]["assets"]["preview"]["url"]
        else:
            return "No images found for the given prompt."
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"
    except json.JSONDecodeError:
        return "Error decoding the response from the API."

# Example usage
prompt = "kites"
image_url = generate_image(prompt)
print(image_url)
