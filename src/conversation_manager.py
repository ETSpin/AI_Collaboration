"""
Class: ConversationManager
Author: MORS
Date: 22 MAR 26

Description:
This class is a utility that will act on conversation objects

Usage:
TBD...

"""


class ConversationManager:

    # Accept user's input - will need to flesh this out later -- error checking and the like
    @staticmethod
    def add_user_message(conversation, input_message):
        conversation._messages.append({"role": "user", "content" : input_message})

    # Accept ai's response - will need to flesh this out later -- error checking and the like
    @staticmethod
    def add_ai_response(conversation, response):
        conversation._messages.append({"role": "assistant", "content" : response.message.content})
        conversation.updated_at = response.created_at


    @staticmethod
    def add_ai_metadata(conversation, response):
        pass

    # Reset or reinitialize the conversation as needed
    @staticmethod
    def reset_conversation(conversation):
        pass

    #Return the model name for this conversation
    @staticmethod
    def get_model(conversation):
        return conversation.model_name

    #Set the model name (validation can go here later)
    @staticmethod
    def set_model(conversation, new_model):
        conversation.model_name = new_model

    #Return the conversation history
    @staticmethod
    def history(conversation):
        return conversation.messages
    
    #Return the persona (temperature) for this conversation
    @staticmethod
    def get_temperature(conversation):
        return conversation.persona
    
    #Set the persona (temperature) for this conversation
    @staticmethod
    def set_temperature(conversation, value):
        conversation.persona = value

    #Return the overview of this conversation
    @staticmethod
    def get_conversation_info(conversation):
        return str(conversation)
    
    #Return the available models - this is spawned as a subprocess to get to the Ollama Cli
    #Subprocess is imported here because we won't use it that often (if ever) so this saves some space
    @staticmethod
    def get_available_models():
        import subprocess

        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            lines = result.stdout.strip().split("\n")
            models = []

            # Skip header line
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    models.append(parts[0])  # model name

            return models

        except Exception as e:
            return(f"Error retrieving model list: {e}")



