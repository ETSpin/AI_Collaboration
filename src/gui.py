"""
Class: Gui
Author: Largely AI generated, refined by MORS
Date: 4 APR 26

Description:
Graphical User Interface for interacting with the AppController and underlying
conversation system. Provides a complete visual front-end for chat, persona
visualization, model settings, system prompt editing, and metadata inspection.

The GUI is intentionally kept “dumb” — it does not run model logic or mutate
conversation internals directly. Instead, it delegates all business logic to
AppController and ConversationManager. Its responsibilities are limited to
rendering, user input capture, and visual state updates.

Responsibilities:
   - Render the chat transcript and append new user/AI messages.
   - Capture user input and forward it to AppController for processing.
   - Display persona artwork and update it dynamically based on temperature.
   - Provide a temperature slider and propagate changes to the active conversation.
   - Display model settings, system prompt text, and conversation metadata.
   - Maintain a clean, modular layout for future expansion (tools, notes, etc.).
   - Provide hooks for AppController to push updates (chat + context panels).

Not Responsible For:
   - Running the model or generating responses.
   - Managing conversation lifecycle or switching conversations.
   - Mutating message history or model options directly (beyond temperature).
   - Managing filesystem context or ingesting external files.
   - Implementing business logic, dispatching commands, or REPL behavior.

Public API Contract:

   Constructor:
     - __init__(root, controller)
         Inputs: Tk root window, AppController instance
         Outputs: Gui instance
         Notes: builds all widgets, loads persona frames, initializes layout

   Instance Methods:

     - load_frames()
         Inputs: none
         Outputs: list[Image]
         Notes: loads and resizes persona animation frames from disk

     - _create_widgets()
         Inputs: none
         Outputs: none
         Notes: constructs all GUI widgets and places them on the canvas

     - on_button_1_click()
         Inputs: none
         Outputs: none
         Notes: captures user input, sends it to controller, updates chat display

     - on_temp_change(value)
         Inputs: slider value (string/float)
         Outputs: none
         Notes: updates persona image and writes temperature into conversation options

     - update_persona_image(temp)
         Inputs: temperature (float)
         Outputs: none
         Notes: renders a drift-proof persona frame with glow effects

     - update_context_panel()
         Inputs: none
         Outputs: none
         Notes: refreshes metadata panel with conversation ID, persona, model, options
"""


import os
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageFilter, ImageTk

from dispatcher import conversation_dispatch, system_dispatch


class Gui:
    def __init__(self, root, controller):        
        self.root = root
        self.root.title("gui")
        self.root.geometry("1280x1410")
        self.root.resizable(True, True)

        self.controller = controller #connect the gui to the App_Controller

        # ============================
        # FRAME CONFIG
        # ============================
        self.frame_count = 10
        self.frame_width = 360
        self.frame_height = 250

        # Load individual frames
        self.frames = self.load_frames()

        self._create_widgets()

        # Initialize persona image at temp = 0.0
        self.update_persona_image(0.0)

    # ============================================================
    # LOAD INDIVIDUAL FRAME FILES
    # ============================================================
    def load_frames(self):
        frames = []

        for i in range(self.frame_count):
            filename = f"./assets/Scientist Frame {i}.png"

            if not os.path.exists(filename):
                raise FileNotFoundError(f"Missing frame file: {filename}")

            img = Image.open(filename).convert("RGBA")

            # Resize to 360x250
            img = img.resize((self.frame_width, self.frame_height), Image.LANCZOS)

            frames.append(img)

        return frames

    # ============================================================
    # GUI WIDGETS
    # ============================================================
    def _create_widgets(self):

        # ============================
        # LEFT SIDE — CHAT + INPUT
        # ============================

        self.chat_display = tk.Text(
            self.root, font=("Arial", 12), wrap="word",
            bg="#ffffff", fg="#000000"
        )
        self.chat_display.place(x=10, y=20, width=870, height=1220)

        self.entry_1 = tk.Text(
            self.root, font=("Arial", 12),
            bg="#ffffff", fg="#000000",
            wrap="word"
        )
        self.entry_1.place(x=10, y=1260, width=740, height=120)
        #self.entry_1.insert(0, "Enter text...")

        self.button_1 = tk.Button(
            self.root, text="Button", font=("Arial", 12),
            command=self.on_button_1_click
        )
        self.button_1.place(x=760, y=1260, width=120, height=120)

        # ============================
        # RIGHT COLUMN — AI CONTROL STACK
        # ============================

        RIGHT_X = 900
        RIGHT_W = 360

        # --------------------------------
        # 1. AI PERSONA PANEL (Top)
        # --------------------------------
        self.image_label = tk.Label(self.root, bg="#ffffff")
        self.image_label.place(x=RIGHT_X, y=20, width=RIGHT_W, height=250)

        # Temperature slider label
        self.temp_label = tk.Label(
            self.root, text="Creativity / Temperature",
            font=("Arial", 12), anchor="center"
        )
        self.temp_label.place(x=RIGHT_X, y=280, width=RIGHT_W, height=25)

        # Temperature slider (with callback)
        self.slider_temp = tk.Scale(
            self.root,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            length=RIGHT_W,
            font=("Arial", 10),
            command=self.on_temp_change
        )
        self.slider_temp.place(x=RIGHT_X, y=310, width=RIGHT_W, height=50)

        # --------------------------------
        # 2. MODEL SETTINGS PANEL
        # --------------------------------
        self.label_settings = tk.Label(
            self.root, text="Model Settings",
            font=("Arial", 14, "bold"), anchor="w"
        )
        self.label_settings.place(x=RIGHT_X, y=370, width=RIGHT_W, height=30)

        self.label_2 = tk.Label(
            self.root, text="System Prompt:",
            font=("Arial", 12), anchor="w"
        )
        self.label_2.place(x=RIGHT_X, y=410, width=120, height=30)

        self.combobox_2 = ttk.Combobox(
            self.root, values=["Option 1", "Option 2", "Option 3"],
            state="readonly"
        )
        self.combobox_2.place(x=RIGHT_X + 130, y=410, width=230, height=30)
        self.combobox_2.current(0)

        self.label_1 = tk.Label(
            self.root, text="Mode:",
            font=("Arial", 12), anchor="w"
        )
        self.label_1.place(x=RIGHT_X, y=450, width=120, height=30)

        self.combobox_1 = ttk.Combobox(
            self.root, values=["Option 1", "Option 2", "Option 3"],
            state="readonly"
        )
        self.combobox_1.place(x=RIGHT_X + 130, y=450, width=230, height=30)
        self.combobox_1.current(0)

        # --------------------------------
        # 3. SYSTEM PROMPT PANEL
        # --------------------------------
        self.label_system = tk.Label(
            self.root, text="System Prompt",
            font=("Arial", 14, "bold"), anchor="w"
        )
        self.label_system.place(x=RIGHT_X, y=500, width=RIGHT_W, height=30)

        self.system = tk.Text(
            self.root, font=("Arial", 12), wrap="word",
            bg="#ffffff", fg="#000000"
        )
        self.system.place(x=RIGHT_X, y=540, width=RIGHT_W, height=220)

        # --------------------------------
        # 4. CONTEXT PANEL
        # --------------------------------
        self.label_context = tk.Label(
            self.root, text="Context / Metadata",
            font=("Arial", 14, "bold"), anchor="w"
        )
        self.label_context.place(x=RIGHT_X, y=780, width=RIGHT_W, height=30)

        self.textarea_3 = tk.Text(
            self.root, font=("Arial", 12), wrap="word",
            bg="#ffffff", fg="#000000"
        )
        self.textarea_3.place(x=RIGHT_X, y=820, width=RIGHT_W, height=260)

        # --------------------------------
        # 5. NOTES / FUTURE TOOLS PANEL
        # --------------------------------
        self.label_notes = tk.Label(
            self.root, text="Notes / Future Tools",
            font=("Arial", 14, "bold"), anchor="w"
        )
        self.label_notes.place(x=RIGHT_X, y=1090, width=RIGHT_W, height=30)

        self.textarea_4 = tk.Text(
            self.root, font=("Arial", 12), wrap="word",
            bg="#ffffff", fg="#000000"
        )
        self.textarea_4.place(x=RIGHT_X, y=1130, width=RIGHT_W, height=260)

    # ============================================================
    # UPDATE PERSONA IMAGE (NO DRIFT VERSION)
    # ============================================================
    def update_persona_image(self, temp):
        # 1. Select frame
        index = min(9, max(0, int(temp * 9)))
        frame = self.frames[index]

        # 2. Glow canvas
        GLOW_EXTRA = 60
        VIEW_W = 360
        VIEW_H = self.frame_height

        CANVAS_W = VIEW_W + GLOW_EXTRA
        CANVAS_H = VIEW_H

        bg_color = (
            int(60 + 160 * temp),
            int(60 + 100 * (1 - temp)),
            int(80 + 160 * (1 - temp)),
            255
        )

        glow_canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), bg_color)

        # 3. Blurred glow
        rgb_frame = frame.convert("RGB")
        blurred = rgb_frame.filter(ImageFilter.GaussianBlur(radius=35))

        tint = Image.new("RGB", blurred.size, (
            int(255 * temp),
            int(180 * (1 - temp)),
            int(255 * (1 - temp))
        ))
        blurred = Image.blend(blurred, tint, alpha=0.45).convert("RGBA")

        # 4. Center blurred glow
        glow_x = (CANVAS_W - blurred.width) // 2
        glow_canvas.paste(blurred, (glow_x, 0), blurred)

        # 5. Center crisp frame
        frame_x = (CANVAS_W - frame.width) // 2
        glow_canvas.paste(frame, (frame_x, 0), frame)

        # 6. Crop final viewport
        left = (CANVAS_W - VIEW_W) // 2
        final = glow_canvas.crop((left, 0, left + VIEW_W, CANVAS_H))

        # 7. Display
        self.tk_frame = ImageTk.PhotoImage(final)
        self.image_label.config(image=self.tk_frame)

    # ============================================================
    # BUTTON HANDLER
    # ============================================================
    def on_button_1_click(self):
        text = self.entry_1.get("1.0", "end").strip()
        self.entry_1.delete("1.0", "end")
        
            # NEW: route commands BEFORE anything else
        if text.startswith("/"):
            system_dispatch(text[1:], self.controller.active_conversation)
            self.update_context_panel()
            return

        if text.startswith("-"):
            conversation_dispatch(text[1:], self.controller.active_conversation)
            self.update_context_panel()
            return

        persona = self.controller.active_conversation.persona_dict.get("name", "AI")
        
        self.chat_display.insert("end", f"User: {text}\n")
        response = self.controller.run_conversation_turn(text)
        self.chat_display.insert("end", f"{persona}: {response}\n\n")
        self.chat_display.insert("end", "──────────────────────────────\n\n")
        self.chat_display.see("end")

        self.update_context_panel()

    # update the context panel based on the conversation
    def update_context_panel(self):
        if self.controller and self.controller.active_conversation:
            conv = self.controller.active_conversation

            context_text = []
            context_text.append(f"Conversation ID: {conv.conversation_id}")
            context_text.append(f"Persona: {conv.persona_dict.get('name', 'Unknown')}")
            context_text.append(f"Model: {conv.model_name}")
            context_text.append(f"Model max tokens: {conv.tokens_model_max}")

            settings = conv.model_settings

            context_text.append(f"Current num_ctx: {settings.get('num_ctx')}")
            context_text.append(f"Current temperature: {settings.get('temperature')}")
            context_text.append(f"Current top_p: {settings.get('top_p')}")
            context_text.append(f"Current repeat penalty: {settings.get('repeat_penalty')}")



            self.textarea_3.delete("1.0", "end")
            self.textarea_3.insert("end", "\n".join(context_text))

    # Update the persona graphic and slider bar based on the conversation
    def on_temp_change(self, value):
        temp = float(value)
        self.update_persona_image(temp)
        # update model options
        if self.controller and self.controller.active_conversation:
            conv = self.controller.active_conversation
            conv.model_settings["temperature"] = temp
            self.update_context_panel()



if __name__ == "__main__":
    root = tk.Tk()
    app = Gui(root)
    root.mainloop()