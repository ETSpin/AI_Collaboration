"""
Class: ThinkingDisplay
Author: MORS
Date: 22 MAR 26

Description:
Handles the display of model thought process (also called partial or streaming output) in real time
Built to  support a separate UI element for showing the model's "thinking" process - separate from the conversation

Usage:
TBD...
"""

class ThinkingDisplay:

    # Capture a chunk of the model's partial output (i.e., look at it's thinking)
    def capture_partial_output(self, output_chunk):
        pass

    # Update the display with new partial output - ensure clear separation between output chunks for a clear understanding
    def update_display(self, output_chunk, window_id=None):
        pass

    # Clear the display between responses or when requested
    def clear_display(self, window_id=None):
        pass