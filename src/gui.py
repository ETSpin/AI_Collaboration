"""
Class: Gui
Author: MORS
Date: 4 APR 26

Description:
Handles the display of model thought process (also called partial or streaming output) in real time
Built to  support a separate UI element for showing the model's "thinking" process - separate from the conversation

Usage:
TBD...
"""

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageFilter, ImageTk


class Gui:
    def __init__(self, root):
        self.root = root
        self.root.title("gui")
        self.root.geometry("1280x1410")
        self.root.resizable(True, True)

        # Load full sprite sheet (10 frames horizontally)
        self.full_image = Image.open("./assets/Retro Scientist - AI temp model v2.png")
        self.frame_count = 10
        self.frame_height = 250  # target display height

        self.preprocess_sheet()

        self._create_widgets()

        # Initialize persona image at temp = 0.0
        self.update_persona_image(0.0)

    def _create_widgets(self):

        # ============================
        # LEFT SIDE — CHAT + INPUT
        # ============================

        self.chat_display = tk.Text(
            self.root, font=("Arial", 12), wrap="word",
            bg="#ffffff", fg="#000000"
        )
        self.chat_display.place(x=10, y=20, width=870, height=1220)

        self.entry_1 = tk.Entry(
            self.root, font=("Arial", 12),
            bg="#ffffff", fg="#000000"
        )
        self.entry_1.place(x=10, y=1260, width=740, height=120)
        self.entry_1.insert(0, "Enter text...")

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
            command=self.on_temp_change   # <-- callback wired here
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

    # ============================
    # IMAGE UPDATE LOGIC
    # ============================

    def on_temp_change(self, value):
        """Slider callback — updates persona image continuously."""
        self.update_persona_image(float(value))

    def update_persona_image(self, temp):
        # 1. Determine which frame to show
        index = int(temp * (self.frame_count - 1))
        frame_width = self.full_image.width // self.frame_count

        x0 = index * frame_width
        x1 = x0 + frame_width

        frame = self.full_image.crop((x0, 0, x1, self.full_image.height))

        # 2. Crop top/bottom
        crop_top = 275
        crop_bottom = 300
        frame = frame.crop((0, crop_top, frame.width, frame.height - crop_bottom))

        # 3. Resize to 250px height
        target_h = 250
        scale_factor = target_h / frame.height
        new_w = int(frame.width * scale_factor)
        frame = frame.resize((new_w, target_h), Image.LANCZOS)

        # -----------------------------------
        # 4. Build glow canvas (half as wide as before)
        # -----------------------------------
        glow_extra = 60  # was 120; now half as thick
        glow_w = 360 + glow_extra
        glow_h = target_h

        # Temperature-based background tint
        bg_color = (
            int(60 + 160 * temp),        # red
            int(60 + 100 * (1 - temp)),  # green
            int(80 + 160 * (1 - temp))   # blue
        )

        glow = Image.new("RGB", (glow_w, glow_h), bg_color)

        # 5. Create blurred glow source
        blurred = frame.filter(ImageFilter.GaussianBlur(radius=35))

        # Tint the blurred glow
        tint = Image.new("RGB", blurred.size, (
            int(255 * temp),
            int(180 * (1 - temp)),
            int(255 * (1 - temp))
        ))
        blurred = Image.blend(blurred, tint, alpha=0.45)

        # Paste blurred glow centered
        glow_x = (glow_w - blurred.width) // 2
        glow.paste(blurred, (glow_x, 0))

        # -----------------------------------
        # 6. Paste the frame centered on top
        # -----------------------------------
        final = glow.copy()
        frame_x = (glow_w - frame.width) // 2
        final.paste(frame, (frame_x, 0))

        # -----------------------------------
        # 7. Crop final to 360px viewport
        # -----------------------------------
        left = (glow_w - 360) // 2
        final = final.crop((left, 0, left + 360, target_h))

        # 8. Display
        self.tk_frame = ImageTk.PhotoImage(final)
        self.image_label.config(image=self.tk_frame)





    def preprocess_sheet(self):
        img = self.full_image

        # --- 1. Crop top and bottom to remove whitespace ---
        crop_top = 275
        crop_bottom = 300
        img = img.crop((0, crop_top, img.width, img.height - crop_bottom))

        # --- 2. Resize height to 250px (viewport height) ---
        target_h = 250
        scale_factor = target_h / img.height
        new_w = int(img.width * scale_factor)
        img = img.resize((new_w, target_h), Image.LANCZOS)

        # Store the processed sheet
        self.processed_sheet = img



    # ============================
    # BUTTON HANDLER
    # ============================

    def on_button_1_click(self):
        pass




if __name__ == "__main__":
    root = tk.Tk()
    app = Gui(root)
    root.mainloop()