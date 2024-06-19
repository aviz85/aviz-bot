from whatsapp_chatbot_python import GreenAPIBot, Notification
from whatsapp_chatbot_python.filters import TEXT_TYPES
import os

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
            response = chatbot.get_chat_response(user_message)
            notification.answer(response)
            print(f"Answered message: {response}")

    bot.run_forever()
