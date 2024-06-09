import json

class Extractor:
    def __init__(self, client):
        self.client = client

    def extract_info(self, user_message, chat_response, required_info, chat_history):
        # Build the full chat history into the prompt
        history_text = ""
        for message in chat_history:
            role = message['role']
            content = message['content']
            history_text += f"{role.capitalize()} message: \"{content}\"\n"

        # Include the latest user message and assistant response
        history_text += f"User message: \"{user_message}\"\n"
        history_text += f"Assistant response: \"{chat_response}\"\n"

        # Construct the prompt with required information details
        prompt = f"""
        Given the following chat history, extract the requested information and provide it in JSON format. Be conservative and provide information only when sure:

        {history_text}

        Requested information:
        """
        for info in required_info:
            prompt += f"- {info}: The expected value for {info}.\n"
        
        prompt += "Provide the extracted information in the following JSON format:\n"
        prompt += "{\n"
        for info in required_info:
            prompt += f'  "{info}": <value>,\n'
        prompt += "}\n"

        # Make the API call to OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts requested information from a conversation and provides it in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        json_output = response.choices[0].message.content.strip()
        print(json_output)
        try:
            extracted_info = json.loads(json_output)
            return extracted_info
        except json.JSONDecodeError:
            print("Error: Invalid JSON format returned by the AI model.")
            return {}

