import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import storage
from wheel_widget import WheelWidget

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

        # Load initial empty state
        self.update_entry_list()

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

    def update_entry_list(self):
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
            btn_del.pack(side="right")

    def spin_wheel(self):
        self.wheel.hide_overlay()
        self.lbl_result.configure(text="Spinning...")
        self.btn_spin.configure(state="disabled")
        self.wheel.spin(callback=self.on_spin_end)

    def on_spin_end(self, winner):
        self.lbl_result.configure(text=f"Winner: {winner['label']}!")
        self.btn_spin.configure(state="normal")
        self.wheel.show_overlay(winner['label'])

    def save_current_config(self):
        if not self.entries:
            messagebox.showwarning("Warning", "No entries to save!")
            return

        name = simpledialog.askstring("Save Configuration", "Enter a name for this configuration:", initialvalue=self.current_config_name)
        if name:
            storage.save_config(name, self.entries)
            self.current_config_name = name
            self.refresh_configs()
            messagebox.showinfo("Success", f"Saved '{name}' successfully!")

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
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{name}'?"):
            storage.delete_config(name)
            self.refresh_configs()

    def rename_config_action(self, name):
        new_name = simpledialog.askstring("Rename", f"Enter new name for '{name}':", initialvalue=name)
        if new_name and new_name != name:
            storage.rename_config(name, new_name)
            self.refresh_configs()

if __name__ == "__main__":
    app = App()
    app.mainloop()
