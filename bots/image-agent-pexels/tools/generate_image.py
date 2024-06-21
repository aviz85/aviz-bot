import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_image(prompt):
    # Pexels API endpoint for photo search
    url = "https://api.pexels.com/v1/search"
    
    # Get the API key from environment variable
    api_key = os.getenv("PEXELS_API_KEY")
    
    if not api_key:
        return "Error: PEXELS_API_KEY not found in environment variables."
    
    # Headers for the API request
    headers = {
        "Authorization": api_key
    }
    
    # Parameters for the API request
    params = {
        "query": prompt,
        "orientation": "square",
        "per_page": 1  # We only need the first result
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Check if photos are found
        if data["total_results"] > 0:
            # Return the URL of the first photo
            return data["photos"][0]["src"]["original"]
        else:
            return "No images found for the given prompt."
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"