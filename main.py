import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.colorchooser import askcolor
import storage
from wheel_widget import WheelWidget

try:
    import ctypes
except ImportError:
    ctypes = None

def apply_dark_title_bar(window):
    """
    Forces the title bar to be dark on Windows 10/11.
    """
    if ctypes:
        try:
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1) # 1 = True
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), 4)
        except Exception as e:
            pass

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Random Wheel Spinner")
        self.geometry("900x600")

        # Data
        self.entries = [] # List of dicts {'label': str, 'weight': float}
        self.current_config_name = None

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_spinner = self.tab_view.add("Spinner")
        self.tab_configs = self.tab_view.add("Configurations")

        self.setup_spinner_tab()
        self.setup_configs_tab()

        # Load initial state
        self.entries = storage.load_autosave()
        self.update_entry_list()
        self.wheel.set_entries(self.entries)

    def setup_spinner_tab(self):
        self.tab_spinner.grid_columnconfigure(0, weight=1) # Wheel
        self.tab_spinner.grid_columnconfigure(1, weight=0) # Controls
        self.tab_spinner.grid_rowconfigure(0, weight=1)

        # Wheel Area
        self.wheel_frame = ctk.CTkFrame(self.tab_spinner, fg_color="transparent")
        self.wheel_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.wheel = WheelWidget(self.wheel_frame, width=400, height=400, bg="#2B2B2B", highlightthickness=0) 
        self.wheel.pack(expand=True, fill="both")

        # Controls Area
        self.controls_frame = ctk.CTkFrame(self.tab_spinner, width=300)
        self.controls_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.controls_frame.grid_rowconfigure(2, weight=1) # Listbox expands

        # Add Entry
        self.add_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.entry_name = ctk.CTkEntry(self.add_frame, placeholder_text="Entry Name")
        self.entry_name.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.entry_weight = ctk.CTkEntry(self.add_frame, placeholder_text="Weight (1.0)", width=80)
        self.entry_weight.pack(side="left", padx=(0, 5))
        
        self.btn_add = ctk.CTkButton(self.add_frame, text="+", width=40, command=self.add_entry)
        self.btn_add.pack(side="left")

        # Spin Button
        self.btn_spin = ctk.CTkButton(self.controls_frame, text="SPIN THE WHEEL!", height=50, font=("Arial", 16, "bold"), command=self.spin_wheel)
        self.btn_spin.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Entries List
        self.list_frame = ctk.CTkScrollableFrame(self.controls_frame, label_text="Entries")
        self.list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Save Button
        self.btn_save_current = ctk.CTkButton(self.controls_frame, text="Save Configuration", command=self.save_current_config)
        self.btn_save_current.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # Result Label
        self.lbl_result = ctk.CTkLabel(self.tab_spinner, text="", font=("Arial", 24, "bold"))
        self.lbl_result.grid(row=1, column=0, columnspan=2, pady=10)

    def setup_configs_tab(self):
        self.tab_configs.grid_columnconfigure(0, weight=1)
        self.tab_configs.grid_rowconfigure(0, weight=1)

        self.config_list_frame = ctk.CTkScrollableFrame(self.tab_configs, label_text="Saved Configurations")
        self.config_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.config_actions_frame = ctk.CTkFrame(self.tab_configs)
        self.config_actions_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.btn_refresh = ctk.CTkButton(self.config_actions_frame, text="Refresh", command=self.refresh_configs)
        self.btn_refresh.pack(side="left", padx=5)

        self.refresh_configs()

    def add_entry(self):
        name = self.entry_name.get().strip()
        weight_str = self.entry_weight.get().strip()
        
        if not name:
            return
        
        try:
            weight = float(weight_str) if weight_str else 1.0
        except ValueError:
            messagebox.showerror("Error", "Weight must be a number")
            return

        self.entries.append({'label': name, 'weight': weight})
        self.entry_name.delete(0, 'end')
        self.entry_weight.delete(0, 'end')
        self.update_entry_list()
        self.wheel.set_entries(self.entries)

    def remove_entry(self, index):
        del self.entries[index]
        self.update_entry_list()
        self.wheel.set_entries(self.entries)

    def edit_entry(self, index):
        entry = self.entries[index]
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Entry")
        dialog.geometry("350x250")
        
        # Center dialog relative to main window
        x = self.winfo_x() + (self.winfo_width() // 2) - 175
        y = self.winfo_y() + (self.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")
        
        # Make it modal
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        
        # Apply dark title bar fix
        dialog.update()
        apply_dark_title_bar(dialog)
        
        # Grid Layout
        dialog.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_entry = ctk.CTkEntry(dialog)
        name_entry.insert(0, entry['label'])
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(dialog, text="Weight:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        weight_entry = ctk.CTkEntry(dialog)
        weight_entry.insert(0, str(entry['weight']))
        weight_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Color Selection
        current_color = entry.get('color')
        if not current_color:
            # Default to the palette color that would be used
            current_color = self.wheel.colors[index % len(self.wheel.colors)]
            
        self.selected_color = current_color
        
        ctk.CTkLabel(dialog, text="Color:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        color_btn = ctk.CTkButton(dialog, text="", fg_color=current_color, width=40, height=28, border_width=2, border_color="gray")
        
        def pick_color():
            color = askcolor(color=self.selected_color, title="Choose Entry Color")[1]
            if color:
                self.selected_color = color
                color_btn.configure(fg_color=color)
                
        color_btn.configure(command=pick_color)
        color_btn.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        def save():
            new_name = name_entry.get().strip()
            new_weight_str = weight_entry.get().strip()
            
            if not new_name:
                return
            
            try:
                new_weight = float(new_weight_str)
            except ValueError:
                messagebox.showerror("Error", "Weight must be a number")
                return
                
            self.entries[index] = {
                'label': new_name, 
                'weight': new_weight,
                'color': self.selected_color
            }
            self.update_entry_list()
            self.wheel.set_entries(self.entries)
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=20)

    def update_entry_list(self):
        # Save current state
        storage.save_autosave(self.entries)

        # Clear existing widgets in scrollable frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for i, entry in enumerate(self.entries):
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            lbl = ctk.CTkLabel(row, text=f"{entry['label']} (x{entry['weight']})", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            
            btn_del = ctk.CTkButton(row, text="X", width=30, fg_color="#FF5555", hover_color="#CC0000", 
                                    command=lambda idx=i: self.remove_entry(idx))
            btn_del.pack(side="right", padx=(2, 0))
            
            btn_edit = ctk.CTkButton(row, text="✎", width=30, fg_color="#3B8ED0", hover_color="#1F6AA5",
                                    command=lambda idx=i: self.edit_entry(idx))
            btn_edit.pack(side="right", padx=(0, 2))
            
        # Update spin button state
        if self.entries:
            self.btn_spin.configure(state="normal")
        else:
            self.btn_spin.configure(state="disabled")

    def spin_wheel(self):
        self.wheel.hide_overlay()
        self.lbl_result.configure(text="Spinning...")
        self.btn_spin.configure(state="disabled")
        self.wheel.spin(callback=self.on_spin_end)

    def on_spin_end(self, winner):
        self.lbl_result.configure(text=f"Winner: {winner['label']}!")
        self.btn_spin.configure(state="normal" if self.entries else "disabled")
        self.wheel.show_notification("WINNER!", winner['label'])

    def save_current_config(self):
        if not self.entries:
            messagebox.showwarning("Warning", "No entries to save!")
            return

        # Custom Dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Save Configuration")
        dialog.geometry("300x160")
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 80
        dialog.geometry(f"+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        
        # Apply dark title bar fix
        dialog.update()
        apply_dark_title_bar(dialog)
        
        ctk.CTkLabel(dialog, text="Enter configuration name:").pack(pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog)
        if self.current_config_name:
            name_entry.insert(0, self.current_config_name)
        name_entry.pack(pady=5, padx=20, fill="x")
        name_entry.focus_set()
        
        def on_save():
            name = name_entry.get().strip()
            if name:
                storage.save_config(name, self.entries)
                self.current_config_name = name
                self.refresh_configs()
                
                self.tab_view.set("Spinner")
                self.wheel.show_notification("Saved!", f"Configuration '{name}'\nsaved successfully!", color="#2CC985")
                dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="Save", command=on_save, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, width=80, fg_color="transparent", border_width=1, border_color="gray").pack(side="left", padx=5)
        
        # Allow Enter key to save
        dialog.bind("<Return>", lambda e: on_save())

    def refresh_configs(self):
        # Clear list
        for widget in self.config_list_frame.winfo_children():
            widget.destroy()
            
        configs = storage.list_configs()
        
        for name in configs:
            row = ctk.CTkFrame(self.config_list_frame)
            row.pack(fill="x", pady=5)
            
            lbl = ctk.CTkLabel(row, text=name, font=("Arial", 14))
            lbl.pack(side="left", padx=10)
            
            # Buttons
            btn_del = ctk.CTkButton(row, text="Delete", width=60, fg_color="#FF5555", hover_color="#CC0000",
                                    command=lambda n=name: self.delete_config_action(n))
            btn_del.pack(side="right", padx=5)
            
            btn_rename = ctk.CTkButton(row, text="Rename", width=60,
                                       command=lambda n=name: self.rename_config_action(n))
            btn_rename.pack(side="right", padx=5)
            
            btn_load = ctk.CTkButton(row, text="Load", width=60, fg_color="#2CC985", hover_color="#229966",
                                     command=lambda n=name: self.load_config_action(n))
            btn_load.pack(side="right", padx=5)

    def load_config_action(self, name):
        data = storage.load_config(name)
        if data:
            self.entries = data.get('entries', [])
            self.current_config_name = data.get('name', name)
            self.update_entry_list()
            self.wheel.set_entries(self.entries)
            self.tab_view.set("Spinner") # Switch tab
            self.lbl_result.configure(text=f"Loaded: {name}")

    def delete_config_action(self, name):
        # Custom Dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("300x120")
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 60
        dialog.geometry(f"+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        
        # Apply dark title bar fix
        dialog.update()
        apply_dark_title_bar(dialog)
        
        ctk.CTkLabel(dialog, text=f"Are you sure you want to delete\n'{name}'?", font=("Arial", 14)).pack(pady=(20, 10))
        
        def on_delete():
            storage.delete_config(name)
            self.refresh_configs()
            dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Delete", command=on_delete, width=80, fg_color="#FF5555", hover_color="#CC0000").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, width=80, fg_color="transparent", border_width=1, border_color="gray").pack(side="left", padx=5)

    def rename_config_action(self, name):
        # Custom Dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Rename Configuration")
        dialog.geometry("300x160")
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 80
        dialog.geometry(f"+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        
        # Apply dark title bar fix
        dialog.update()
        apply_dark_title_bar(dialog)
        
        ctk.CTkLabel(dialog, text=f"Enter new name for '{name}':").pack(pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog)
        name_entry.insert(0, name)
        name_entry.pack(pady=5, padx=20, fill="x")
        name_entry.focus_set()
        name_entry.select_range(0, 'end')
        
        def on_rename():
            new_name = name_entry.get().strip()
            if new_name and new_name != name:
                storage.rename_config(name, new_name)
                self.refresh_configs()
                dialog.destroy()
            elif new_name == name:
                dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="Rename", command=on_rename, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, width=80, fg_color="transparent", border_width=1, border_color="gray").pack(side="left", padx=5)
        
        # Allow Enter key to save
        dialog.bind("<Return>", lambda e: on_rename())

if __name__ == "__main__":
    app = App()
    app.mainloop()
