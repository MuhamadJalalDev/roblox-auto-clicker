import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import json
import os
import webbrowser
from clicker import AutoClicker

CONFIG_FILE = "config.json"

# Initialize appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Logicate Autoclicker - Roblox Edition")
        self.geometry("520x780")  # Increased height to accommodate new elements
        self.resizable(False, False)

        self.clicker = AutoClicker()
        self.update_loop_running = True

        self.load_config()
        self.build_ui()
        self.start_status_updater()

    def open_donation_link(self):
        """Open PayPal donation link in browser"""
        try:
            webbrowser.open("https://www.paypal.me/SaniHussain215")
            messagebox.showinfo("Thank You!", "Thank you for considering a donation! Your support helps keep this project alive.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open donation link: {e}")

    def build_ui(self):
        # Create scrollable frame for all content
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=480, height=730)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Header with Donate Button ---
        header_frame = ctk.CTkFrame(self.scrollable_frame)
        header_frame.pack(pady=10, padx=10, fill="x")
        
        # Title
        title_label = ctk.CTkLabel(header_frame, text="AutoClicker Pro - Roblox Edition", 
                                  font=("Segoe UI", 20, "bold"))
        title_label.pack(pady=(10, 5))
        
        # Donate Button
        self.donate_button = ctk.CTkButton(header_frame, text="💝 Support Development - Donate", 
                                          command=self.open_donation_link, height=35,
                                          font=("Segoe UI", 12, "bold"),
                                          fg_color=("green", "darkgreen"),
                                          hover_color=("lightgreen", "forestgreen"))
        self.donate_button.pack(pady=5, padx=20, fill="x")

        # --- Game Presets ---
        preset_frame = ctk.CTkFrame(self.scrollable_frame)
        preset_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(preset_frame, text="🎮 Game Presets", font=("Segoe UI", 18, "bold")).pack(pady=(10, 5))

        presets = [
            "Custom",
            "Pet Sim 99 - Egg Hatching",
            "Blox Fruits - Mastery Farm", 
            "Adopt Me - Pet Tasks",
            "Tapping Legends - Max CPS",
            "Bee Swarm - Pollen Collection",
            "Murder Mystery 2 - Combat",
            "Anime Fighting Sim - Training",
            "A Universal Time - Farming"
        ]

        self.preset_menu = ctk.CTkOptionMenu(preset_frame, values=presets, 
                                           command=self.load_preset, width=300)
        self.preset_menu.set(self.clicker.current_preset)
        self.preset_menu.pack(pady=5)

        # --- Click Pattern Settings ---
        pattern_frame = ctk.CTkFrame(self.scrollable_frame)
        pattern_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(pattern_frame, text="🎯 Click Pattern", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

        patterns = ["single", "area", "multi_point", "circular"]
        self.pattern_menu = ctk.CTkOptionMenu(pattern_frame, values=patterns,
                                            command=self.set_click_pattern)
        self.pattern_menu.set(self.clicker.click_pattern)
        self.pattern_menu.pack(pady=5)

        # Area bounds (for area clicking)
        self.area_frame = ctk.CTkFrame(pattern_frame)
        self.area_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(self.area_frame, text="Area Bounds (X1, Y1, X2, Y2):").pack()
        
        bounds_container = ctk.CTkFrame(self.area_frame)
        bounds_container.pack(pady=5)
        
        self.x1_entry = ctk.CTkEntry(bounds_container, width=70, placeholder_text="X1")
        self.y1_entry = ctk.CTkEntry(bounds_container, width=70, placeholder_text="Y1")
        self.x2_entry = ctk.CTkEntry(bounds_container, width=70, placeholder_text="X2")
        self.y2_entry = ctk.CTkEntry(bounds_container, width=70, placeholder_text="Y2")
        
        self.x1_entry.pack(side="left", padx=2)
        self.y1_entry.pack(side="left", padx=2)
        self.x2_entry.pack(side="left", padx=2)
        self.y2_entry.pack(side="left", padx=2)

        # Load current area bounds
        x1, y1, x2, y2 = self.clicker.area_bounds
        self.x1_entry.insert(0, str(x1))
        self.y1_entry.insert(0, str(y1))
        self.x2_entry.insert(0, str(x2))
        self.y2_entry.insert(0, str(y2))

        # Circular settings
        self.circular_frame = ctk.CTkFrame(pattern_frame)
        self.circular_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(self.circular_frame, text="Circular Pattern:").pack()
        
        circ_container = ctk.CTkFrame(self.circular_frame)
        circ_container.pack(pady=5)
        
        ctk.CTkLabel(circ_container, text="Center X:").pack(side="left")
        self.circ_x_entry = ctk.CTkEntry(circ_container, width=70)
        self.circ_x_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(circ_container, text="Y:").pack(side="left")
        self.circ_y_entry = ctk.CTkEntry(circ_container, width=70)
        self.circ_y_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(circ_container, text="Radius:").pack(side="left")
        self.radius_entry = ctk.CTkEntry(circ_container, width=70)
        self.radius_entry.pack(side="left", padx=5)

        # Load circular settings
        cx, cy = self.clicker.circular_center
        self.circ_x_entry.insert(0, str(cx))
        self.circ_y_entry.insert(0, str(cy))
        self.radius_entry.insert(0, str(self.clicker.circular_radius))

        # --- Basic Settings ---
        basic_frame = ctk.CTkFrame(self.scrollable_frame)
        basic_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(basic_frame, text="⚙️ Basic Settings", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

        # Mouse Button
        button_container = ctk.CTkFrame(basic_frame)
        button_container.pack(pady=5, fill="x")
        ctk.CTkLabel(button_container, text="Mouse Button:").pack()
        self.mouse_button = ctk.CTkOptionMenu(button_container, values=["left", "right", "middle"], 
                                            command=self.set_mouse_button)
        self.mouse_button.set(self.clicker.mouse_button)
        self.mouse_button.pack(pady=5)

        # Click Type
        click_container = ctk.CTkFrame(basic_frame)
        click_container.pack(pady=5, fill="x")
        ctk.CTkLabel(click_container, text="Click Type:").pack()
        self.click_type = ctk.CTkOptionMenu(click_container, values=["Single (1)", "Double (2)", "Triple (3)"], 
                                          command=self.set_click_type)
        self.click_type.set(f"Single (1)" if self.clicker.click_type == 1 else 
                           f"Double (2)" if self.clicker.click_type == 2 else "Triple (3)")
        self.click_type.pack(pady=5)

        # Follow Mouse
        self.follow_mouse = ctk.CTkCheckBox(basic_frame, text="Follow Mouse Cursor", 
                                          command=self.toggle_follow_mouse)
        if self.clicker.follow_mouse:
            self.follow_mouse.select()
        self.follow_mouse.pack(pady=5)

        # Fixed Position
        pos_container = ctk.CTkFrame(basic_frame)
        pos_container.pack(pady=5, fill="x")
        ctk.CTkLabel(pos_container, text="Fixed Position (X, Y):").pack()
        
        pos_subframe = ctk.CTkFrame(pos_container)
        pos_subframe.pack(pady=5)
        
        self.x_entry = ctk.CTkEntry(pos_subframe, width=80, placeholder_text="X")
        self.y_entry = ctk.CTkEntry(pos_subframe, width=80, placeholder_text="Y")
        self.x_entry.insert(0, str(self.clicker.fixed_position[0]))
        self.y_entry.insert(0, str(self.clicker.fixed_position[1]))
        self.x_entry.pack(side="left", padx=5)
        self.y_entry.pack(side="left", padx=5)

        # --- Timing Control ---
        timing_frame = ctk.CTkFrame(self.scrollable_frame)
        timing_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(timing_frame, text="⏱️ Timing Control", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

        self.delay_label = ctk.CTkLabel(timing_frame, text=f"Delay: {self.clicker.base_delay:.3f}s")
        self.delay_label.pack()
        
        self.delay_slider = ctk.CTkSlider(timing_frame, from_=0.001, to=1.0, number_of_steps=100, 
                                        command=self.set_delay)
        self.delay_slider.set(self.clicker.base_delay)
        self.delay_slider.pack(pady=5, padx=10, fill="x")

        self.random_delay = ctk.CTkCheckBox(timing_frame, text="Randomize Delay (±30%)", 
                                          command=self.toggle_random)
        if self.clicker.randomize_delay:
            self.random_delay.select()
        self.random_delay.pack(pady=5)

        self.gradual_speed = ctk.CTkCheckBox(timing_frame, text="Gradual Speed Changes", 
                                           command=self.toggle_gradual_speed)
        if self.clicker.gradual_speed:
            self.gradual_speed.select()
        self.gradual_speed.pack(pady=5)

        # --- Burst Control ---
        burst_frame = ctk.CTkFrame(self.scrollable_frame)
        burst_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(burst_frame, text="💥 Burst Control", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

        self.burst_mode = ctk.CTkCheckBox(burst_frame, text="Enable Burst Mode", 
                                        command=self.toggle_burst)
        if self.clicker.burst_mode:
            self.burst_mode.select()
        self.burst_mode.pack(pady=5)

        self.burst_label = ctk.CTkLabel(burst_frame, text=f"Burst Size: {self.clicker.burst_size}")
        self.burst_label.pack()
        
        self.burst_slider = ctk.CTkSlider(burst_frame, from_=1, to=20, number_of_steps=19, 
                                        command=self.set_burst_size)
        self.burst_slider.set(self.clicker.burst_size)
        self.burst_slider.pack(pady=5, padx=10, fill="x")

        # --- Safety Features ---
        safety_frame = ctk.CTkFrame(self.scrollable_frame)
        safety_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(safety_frame, text="🛡️ Safety Features", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

        self.roblox_only = ctk.CTkCheckBox(safety_frame, text="Only Click When Roblox is Active", 
                                         command=self.toggle_roblox_only)
        if self.clicker.roblox_only:
            self.roblox_only.select()
        self.roblox_only.pack(pady=5)

        self.auto_breaks = ctk.CTkCheckBox(safety_frame, text="Automatic Breaks (10-15 min intervals)", 
                                         command=self.toggle_auto_breaks)
        if self.clicker.auto_breaks:
            self.auto_breaks.select()
        self.auto_breaks.pack(pady=5)

        self.mouse_jitter = ctk.CTkCheckBox(safety_frame, text="Mouse Jitter (Humanization)", 
                                          command=self.toggle_mouse_jitter)
        if self.clicker.mouse_jitter:
            self.mouse_jitter.select()
        self.mouse_jitter.pack(pady=5)

        # Session Limit
        session_container = ctk.CTkFrame(safety_frame)
        session_container.pack(pady=5, fill="x")
        ctk.CTkLabel(session_container, text="Session Limit (minutes, 0 = no limit):").pack()
        self.session_entry = ctk.CTkEntry(session_container, width=100)
        self.session_entry.insert(0, str(self.clicker.session_limit))
        self.session_entry.pack(pady=5)

        # --- Control Buttons ---
        control_frame = ctk.CTkFrame(self.scrollable_frame)
        control_frame.pack(pady=20, padx=10, fill="x")
        
        self.toggle_button = ctk.CTkButton(control_frame, text="🚀 Start Clicking (F6)", 
                                         command=self.toggle_clicker, height=50,
                                         font=("Segoe UI", 16, "bold"))
        self.toggle_button.pack(pady=10, fill="x")

        self.panic_button = ctk.CTkButton(control_frame, text="🚨 PANIC STOP (F8)", 
                                        command=self.panic_stop, height=35,
                                        font=("Segoe UI", 12, "bold"),
                                        fg_color=("red", "darkred"))
        self.panic_button.pack(pady=5, fill="x")

        # --- Stats ---
        stats_frame = ctk.CTkFrame(self.scrollable_frame)
        stats_frame.pack(pady=10, padx=10, fill="x")
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="📊 Clicks: 0 | Elapsed: 0s | Preset: Custom", 
                                      font=("Segoe UI", 12))
        self.stats_label.pack(pady=15)

        self.roblox_status = ctk.CTkLabel(stats_frame, text="🎮 Roblox Status: Checking...", 
                                        font=("Segoe UI", 10))
        self.roblox_status.pack(pady=5)

        # --- Theme Toggle ---
        self.theme_toggle = ctk.CTkSwitch(self.scrollable_frame, text="☀️ Light Mode", command=self.toggle_theme)
        self.theme_toggle.pack(pady=15)

        # --- Footer with Copyright ---
        footer_frame = ctk.CTkFrame(self.scrollable_frame)
        footer_frame.pack(pady=10, padx=10, fill="x")
        
        # Copyright label
        copyright_label = ctk.CTkLabel(footer_frame, text="© 2025 All rights are reserved Logicate", 
                                     font=("Segoe UI", 14),
                                     text_color=("gray60", "gray40"))
        copyright_label.pack(pady=10)

        # Update UI based on current pattern
        self.update_pattern_ui()

    def load_preset(self, preset_name):
        if preset_name != "Custom":
            self.clicker.load_preset(preset_name)
            self.update_ui_from_clicker()
            messagebox.showinfo("Preset Loaded", f"Successfully loaded {preset_name} preset")

    def update_ui_from_clicker(self):
        """Update all UI elements to match current clicker settings"""
        # Update pattern settings
        self.pattern_menu.set(self.clicker.click_pattern)
        self.update_pattern_ui()
        
        # Update area bounds
        x1, y1, x2, y2 = self.clicker.area_bounds
        self.x1_entry.delete(0, 'end')
        self.x1_entry.insert(0, str(x1))
        self.y1_entry.delete(0, 'end')
        self.y1_entry.insert(0, str(y1))
        self.x2_entry.delete(0, 'end')
        self.x2_entry.insert(0, str(x2))
        self.y2_entry.delete(0, 'end')
        self.y2_entry.insert(0, str(y2))
        
        # Update circular settings
        cx, cy = self.clicker.circular_center
        self.circ_x_entry.delete(0, 'end')
        self.circ_x_entry.insert(0, str(cx))
        self.circ_y_entry.delete(0, 'end')
        self.circ_y_entry.insert(0, str(cy))
        self.radius_entry.delete(0, 'end')
        self.radius_entry.insert(0, str(self.clicker.circular_radius))
        
        # Update basic settings
        self.mouse_button.set(self.clicker.mouse_button)
        self.click_type.set(f"Single (1)" if self.clicker.click_type == 1 else 
                          f"Double (2)" if self.clicker.click_type == 2 else "Triple (3)")
        
        if self.clicker.follow_mouse:
            self.follow_mouse.select()
        else:
            self.follow_mouse.deselect()
        
        self.x_entry.delete(0, 'end')
        self.y_entry.delete(0, 'end')
        self.x_entry.insert(0, str(self.clicker.fixed_position[0]))
        self.y_entry.insert(0, str(self.clicker.fixed_position[1]))
        
        # Update timing control
        self.delay_slider.set(self.clicker.base_delay)
        self.delay_label.configure(text=f"Delay: {self.clicker.base_delay:.3f}s")
        
        if self.clicker.randomize_delay:
            self.random_delay.select()
        else:
            self.random_delay.deselect()
        
        if self.clicker.gradual_speed:
            self.gradual_speed.select()
        else:
            self.gradual_speed.deselect()
        
        # Update burst control
        if self.clicker.burst_mode:
            self.burst_mode.select()
        else:
            self.burst_mode.deselect()
        
        self.burst_slider.set(self.clicker.burst_size)
        self.burst_label.configure(text=f"Burst Size: {self.clicker.burst_size}")
        
        # Update safety features
        if self.clicker.roblox_only:
            self.roblox_only.select()
        else:
            self.roblox_only.deselect()
        
        if self.clicker.auto_breaks:
            self.auto_breaks.select()
        else:
            self.auto_breaks.deselect()
        
        if self.clicker.mouse_jitter:
            self.mouse_jitter.select()
        else:
            self.mouse_jitter.deselect()
        
        self.session_entry.delete(0, 'end')
        self.session_entry.insert(0, str(self.clicker.session_limit))
        
        # Update stats
        self.update_stats()

    def update_pattern_ui(self):
        """Show/hide pattern-specific UI elements"""
        pattern = self.clicker.click_pattern
        if pattern == "area":
            self.area_frame.pack(pady=5, fill="x")
            self.circular_frame.pack_forget()
        elif pattern == "circular":
            self.circular_frame.pack(pady=5, fill="x")
            self.area_frame.pack_forget()
        else:
            self.area_frame.pack_forget()
            self.circular_frame.pack_forget()

    def set_click_pattern(self, pattern):
        self.clicker.click_pattern = pattern
        self.update_pattern_ui()

    def set_mouse_button(self, button):
        self.clicker.mouse_button = button

    def set_click_type(self, click_type):
        self.clicker.click_type = int(click_type.split()[1][1])

    def toggle_follow_mouse(self):
        self.clicker.follow_mouse = not self.clicker.follow_mouse
        if not self.clicker.follow_mouse:
            try:
                x = int(self.x_entry.get())
                y = int(self.y_entry.get())
                self.clicker.fixed_position = (x, y)
            except ValueError:
                messagebox.showerror("Error", "Invalid position coordinates")

    def set_delay(self, value):
        self.clicker.base_delay = value
        self.delay_label.configure(text=f"Delay: {value:.3f}s")

    def toggle_random(self):
        self.clicker.randomize_delay = not self.clicker.randomize_delay

    def toggle_gradual_speed(self):
        self.clicker.gradual_speed = not self.clicker.gradual_speed

    def toggle_burst(self):
        self.clicker.burst_mode = not self.clicker.burst_mode

    def set_burst_size(self, value):
        self.clicker.burst_size = int(value)
        self.burst_label.configure(text=f"Burst Size: {int(value)}")

    def toggle_roblox_only(self):
        self.clicker.roblox_only = not self.clicker.roblox_only

    def toggle_auto_breaks(self):
        self.clicker.auto_breaks = not self.clicker.auto_breaks

    def toggle_mouse_jitter(self):
        self.clicker.mouse_jitter = not self.clicker.mouse_jitter

    def toggle_clicker(self):
        if self.clicker.running:
            self.clicker.stop_clicking()
            self.toggle_button.configure(text="🚀 Start Clicking (F6)")
        else:
            self.clicker.start_clicking()
            self.toggle_button.configure(text="⏹️ Stop Clicking (F7)")

    def panic_stop(self):
        self.clicker.panic_stop()
        self.toggle_button.configure(text="🚀 Start Clicking (F6)")

    def update_stats(self):
        status = self.clicker.status()
        clicks = status['clicks']
        elapsed = int(status['elapsed'])
        preset = status['preset']
        roblox_active = "Active" if status['roblox_active'] else "Inactive"
        
        self.stats_label.configure(text=f"📊 Clicks: {clicks} | Elapsed: {elapsed}s | Preset: {preset}")
        self.roblox_status.configure(text=f"🎮 Roblox Status: {roblox_active}")

    def start_status_updater(self):
        def update_loop():
            while self.update_loop_running:
                self.update_stats()
                self.after(1000, self.update_stats)
                time.sleep(1)
        
        threading.Thread(target=update_loop, daemon=True).start()

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_toggle.configure(text="🌙 Dark Mode")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_toggle.configure(text="☀️ Light Mode")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    for key, value in config.items():
                        if hasattr(self.clicker, key):
                            setattr(self.clicker, key, value)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        config = {attr: getattr(self.clicker, attr) for attr in dir(self.clicker) 
                 if not attr.startswith('_') and not callable(getattr(self.clicker, attr))}
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def on_closing(self):
        self.update_loop_running = False
        self.save_config()
        self.clicker.safe_exit()
        self.destroy()

if __name__ == "__main__":
    app = ClickerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()