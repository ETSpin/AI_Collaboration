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
    def reset_conversation(self):
        pass

    #Return the model name for this conversation
    @staticmethod
    def model(conversation):
        return conversation.model_name

    #Set the model name (validation can go here later)
    @staticmethod
    def model_set(conversation, new_model):
        conversation.model_name = new_model

    #Return the conversation history
    @staticmethod
    def history(conversation):
        return conversation.messages