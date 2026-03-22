"""
Class: ContextManager
Author: MORS
Date: 22 MAR 26

Description:
Handles any user provided files and an ability to import data from a library
- Will likley also handle other tool(s) or methods for the model to be able to get additional information (web, other local tools, etc.)

Usage:
TBD...

"""

class ContextManager:
    
    """Accept user's file input """
    def accept_file_upload(self, input_file):
        pass

    """Determine the type of file uploaded by the user """
    def detect_file_type(self, input_file):
        pass

    """Actually extract data from the uploaded file"""
    def extract_data(self, input_file):
        pass

    """Store the the extracted data from the file for the model to be able to access"""
    def store_context_data(self, data):
        pass

    """Returns a list of the user pushed files being used in the context"""
    def get_context_data(self):
        pass

    """Remove the the extracted data from the model's context for future 'thinking' """
    def remove_context_data(self, data):
        pass

    """Load additional context data from a local library or repository"""
    def load_library_files(self, directory):
        pass

    """Returns a list of the local library or repository items used for additional context"""
    def get_library_list(self):
        pass
