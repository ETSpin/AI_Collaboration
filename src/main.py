"""
File: main.py
Author: MORS
Date: 21 MAR 26

Description:
AI experimentation with Ollama and Python

Initial examples/research from https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide 

Usage:

"""
import tkinter as tk

from app_controller import AppController
from gui import Gui

# from context_loader import ContextLoader
# from context_manager import ContextManager


#def main():
#    AppController().app_run()

def main_gui():
    
    controller = AppController()
    root = tk.Tk()
    gui = Gui(root, controller)
    controller.gui = gui

    controller.start_new_conversation("pymetheus")
    gui.update_txt_context_panel()
    gui.slider_temp.set(controller.active_conversation.model_settings["temperature"])
    gui.update_persona_image(controller.active_conversation.model_settings["temperature"])

    root.mainloop()

if __name__ == '__main__':
    main_gui()