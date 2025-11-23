import tkinter as tk
import math
import random
import time
from PIL import Image, ImageDraw, ImageTk, ImageFont

class WheelWidget(tk.Canvas):
    def __init__(self, master, width=400, height=400, **kwargs):
        if 'bg' not in kwargs:
            try:
                bg_color = master.cget("fg_color")
                if isinstance(bg_color, tuple):
                    bg_color = bg_color[1]
                kwargs['bg'] = bg_color
            except:
                kwargs['bg'] = "#2B2B2B"
        if 'highlightthickness' not in kwargs:
            kwargs['highlightthickness'] = 0
        super().__init__(master, width=width, height=height, **kwargs)
        self.entries = []
        self.angle = 0
        self.is_spinning = False
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = min(width, height) / 2 - 20
        
        self.render_scale = 2 # Supersampling for anti-aliasing
        
        self.colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5", "#9B59B6", "#3498DB"]
        
        self.wheel_image = None
        self.tk_image = None
        
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.radius = min(self.width, self.height) / 2 - 20
        self.generate_wheel_image()
        self.draw_wheel()

    def set_entries(self, entries):
        """
        entries: list of dicts {'label': str, 'weight': float}
        """
        self.entries = entries
        self.generate_wheel_image()
        self.draw_wheel()

    def generate_wheel_image(self):
        if not self.entries:
            self.wheel_image = None
            return

        w = int(self.width * self.render_scale)
        h = int(self.height * self.render_scale)
        r = min(w, h) / 2 - (20 * self.render_scale)
        cx = w / 2
        cy = h / 2
        
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        total_weight = sum(e['weight'] for e in self.entries)
        current_angle = 0
        
        # Font setup
        font_size = int(14 * self.render_scale)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        for i, entry in enumerate(self.entries):
            slice_angle = (entry['weight'] / total_weight) * 360
            end_angle = current_angle + slice_angle
            
            color = self.colors[i % len(self.colors)]
            
            # Draw slice (PIL angles are clockwise from 3 o'clock)
            draw.pieslice([cx - r, cy - r, cx + r, cy + r], 
                          start=current_angle, end=end_angle, 
                          fill=color, outline="white", width=int(2*self.render_scale))
            
            # Text handling
            label = entry['label']
            mid_angle = current_angle + slice_angle / 2
            
            # Max width for text (approx 70% of radius)
            max_text_width = r * 0.7
            
            # Truncate text if too long
            text = label
            while font.getlength(text) > max_text_width and len(text) > 0:
                text = text[:-1]
            if len(text) < len(label):
                text = text[:-3] + "..." if len(text) > 3 else "..."
                # Ensure it fits with ellipsis
                while font.getlength(text) > max_text_width and len(text) > 3:
                    text = text[:-4] + "..."
            
            # Draw text onto a separate image to rotate it
            text_w = int(font.getlength(text)) + 20
            text_h = int(font_size * 2)
            txt_img = Image.new("RGBA", (text_w, text_h), (0,0,0,0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((text_w/2, text_h/2), text, font=font, fill="white", anchor="mm")
            
            # Rotate text to match slice
            # We rotate by -mid_angle because PIL rotate is CCW and our angles are CW
            rotated_txt = txt_img.rotate(-mid_angle, expand=True, resample=Image.Resampling.BICUBIC)
            
            # Calculate position
            text_radius = r * 0.65
            rad = math.radians(mid_angle)
            tx = cx + text_radius * math.cos(rad)
            ty = cy + text_radius * math.sin(rad)
            
            # Paste centered
            paste_x = int(tx - rotated_txt.width / 2)
            paste_y = int(ty - rotated_txt.height / 2)
            
            img.paste(rotated_txt, (paste_x, paste_y), rotated_txt)
            
            current_angle += slice_angle
            
        self.wheel_image = img
        self.wheel_image_low = img.resize((self.width, self.height), resample=Image.Resampling.LANCZOS)

    def draw_wheel(self, fast=False):
        self.delete("all")
        
        if not self.entries or not self.wheel_image:
            self.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                             self.center_x + self.radius, self.center_y + self.radius,
                             fill="#E0E0E0", outline="#333")
            self.create_text(self.center_x, self.center_y, text="Add entries\nto spin!", font=("Arial", 14), justify="center")
            return

        if fast and hasattr(self, 'wheel_image_low') and self.wheel_image_low:
            # Fast render for animation
            rotated = self.wheel_image_low.rotate(self.angle, resample=Image.Resampling.BILINEAR, expand=False)
            self.tk_image = ImageTk.PhotoImage(rotated)
        else:
            # High quality render for static display
            rotated = self.wheel_image.rotate(self.angle, resample=Image.Resampling.BICUBIC, expand=False)
            # Resize for display
            resized = rotated.resize((self.width, self.height), resample=Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized)
        
        self.create_image(self.center_x, self.center_y, image=self.tk_image)
        
        # Draw pointer (Triangle at 3 o'clock)
        px = self.center_x + self.radius + 15
        py = self.center_y
        
        self.create_polygon(px, py - 10,
                            px, py + 10,
                            px - 25, py,
                            fill="#333", outline="white", width=2)
        
        # Center hub
        self.create_oval(self.center_x - 10, self.center_y - 10,
                         self.center_x + 10, self.center_y + 10,
                         fill="white", outline="#333")

    def spin(self, callback=None):
        if self.is_spinning or not self.entries:
            return

        self.is_spinning = True
        
        # Random spin duration and total rotation
        duration = random.uniform(3.0, 5.0)
        total_rotation = random.uniform(720, 1440) # At least 2 full spins, up to 4
        
        start_time = time.time()
        start_angle = self.angle
        
        def animate():
            now = time.time()
            elapsed = now - start_time
            
            if elapsed < duration:
                # Ease out cubic
                t = elapsed / duration
                t = 1 - pow(1 - t, 3)
                
                current_rotation = total_rotation * t
                self.angle = (start_angle + current_rotation) % 360
                self.draw_wheel(fast=True)
                self.after(16, animate) # ~60 FPS
            else:
                self.angle = (start_angle + total_rotation) % 360
                self.draw_wheel(fast=False)
                self.is_spinning = False
                if callback:
                    winner = self.get_winner()
                    callback(winner)
        
        animate()

    def get_winner(self):
        # With PIL (CW angles) and rotate (CCW), the pointer at 0 (3 o'clock)
        # corresponds to the slice containing the angle 'self.angle'.
        pointer_angle = self.angle % 360
        
        total_weight = sum(e['weight'] for e in self.entries)
        current_sum = 0
        
        for entry in self.entries:
            slice_angle = (entry['weight'] / total_weight) * 360
            if current_sum <= pointer_angle < current_sum + slice_angle:
                return entry
            current_sum += slice_angle
            
        return self.entries[-1]

    def show_overlay(self, winner_label):
        self.delete("overlay")
        
        # Card dimensions
        card_w, card_h = 300, 116
        
        # Create image with transparency
        img = Image.new("RGBA", (card_w, card_h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        # Draw rounded rect
        # Fill: #333333 (gray20), Outline: #3B8ED0, Width: 2
        draw.rounded_rectangle([0, 0, card_w-1, card_h-1], radius=20, fill="#333333", outline="#3B8ED0", width=3)
        
        # Fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_name = ImageFont.truetype("arial.ttf", 26)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font_title = ImageFont.load_default()
            font_name = ImageFont.load_default()
            font_small = ImageFont.load_default()
            
        # Draw Title
        draw.text((card_w/2, 20), "WINNER!", font=font_title, fill="#3B8ED0", anchor="mm")
        
        # Draw Name (Truncate if needed)
        text = winner_label
        max_width = card_w - 40
        while font_name.getlength(text) > max_width and len(text) > 0:
            text = text[:-1]
        if len(text) < len(winner_label):
            text = text[:-3] + "..."
            
        draw.text((card_w/2, 60), text, font=font_name, fill="white", anchor="mm")
        
        # Draw Dismiss
        draw.text((card_w/2, 100), "(Click to dismiss)", font=font_small, fill="#AAAAAA", anchor="mm")
        
        self.overlay_image = ImageTk.PhotoImage(img)
        self.create_image(self.center_x, self.center_y, image=self.overlay_image, tags="overlay")
        
        # Bind click to dismiss
        self.bind("<Button-1>", self.on_overlay_click)
        
    def hide_overlay(self):
        self.delete("overlay")
        self.unbind("<Button-1>")
        
    def on_overlay_click(self, event):
        self.hide_overlay()
