from whatsapp_chatbot_python import GreenAPIBot, Notification
from whatsapp_chatbot_python.filters import TEXT_TYPES
import os
import re
import requests
from datetime import datetime

def init_whatsapp_green_link(chatbot):
    greenapi_id_instance = os.getenv("GREENAPI_ID_INSTANCE")
    greenapi_access_token = os.getenv("GREENAPI_ACCESS_TOKEN")

    if not greenapi_id_instance or not greenapi_access_token:
        raise ValueError("Green API instance ID and access token must be set in environment variables.")

    bot = GreenAPIBot(greenapi_id_instance, greenapi_access_token)

    @bot.router.message(type_message=TEXT_TYPES)
    def txt_message_handler(notification: Notification) -> None:
        message_data = notification.event["messageData"]
        
        if message_data["typeMessage"] == "textMessage":
            user_message = message_data["textMessageData"]["textMessage"]
            print(f"Received message: {user_message}")
            print(vars(notification))
            response = chatbot.get_chat_response(user_message)
            
            # Detect image in markdown format
            image_pattern = r'!\[.*?\]\((.*?)\)'
            match = re.search(image_pattern, response)
            
            if match:
                # Extract image URL and remove the image markdown from the response
                image_url = match.group(1)
                caption = re.sub(image_pattern, '', response).strip()
                
                # Download the image from the URL
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Create the uploads folder if it doesn't exist
                    uploads_dir = "uploads"
                    os.makedirs(uploads_dir, exist_ok=True)
                    
                    # Save the image with a timestamp in the filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(uploads_dir, f"image_generated_{timestamp}.jpg")
                    with open(image_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    # Respond with the image file and caption
                    notification.answer_with_file(image_path, caption)
                    print(f"Sent image: {image_path}")
                else:
                    # If image download fails, respond with the text message
                    notification.answer(response)
            else:
                notification.answer(response)
            print(f"Answered message: {response}")

    bot.run_forever()
