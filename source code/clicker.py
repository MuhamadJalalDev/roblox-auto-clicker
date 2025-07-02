import pyautogui
import keyboard
import threading
import time
import random
import math
import psutil
import win32gui

class AutoClicker:
    def __init__(self):
        self.running = False
        self.follow_mouse = True
        self.fixed_position = (960, 540)
        self.click_type = 1  # 1 = single, 2 = double, 3 = triple
        self.mouse_button = 'left'
        self.click_limit = 0  # 0 = infinite
        self.base_delay = 0.1  # Base delay between clicks
        self.randomize_delay = True  # Add randomization to delay
        self.burst_mode = True  # Enable burst clicking
        self.burst_size = 5  # Number of clicks in a burst
        self.hotkey_start = 'F6'
        self.hotkey_stop = 'F7'
        self.hotkey_panic = 'F8'  # Panic stop
        self._click_thread = None
        self._hotkeys_bound = False
        
        # Advanced features
        self.click_pattern = "single"  # single, area, multi_point, circular
        self.area_bounds = (900, 500, 1020, 580)  # x1, y1, x2, y2
        self.multi_points = [(960, 540)]  # List of points for multi-point clicking
        self.circular_center = (960, 540)
        self.circular_radius = 50
        self.current_angle = 0
        
        # Safety features
        self.roblox_only = True  # Only click when Roblox is active
        self.auto_breaks = True  # Take random breaks
        self.break_interval = (600, 900)  # Break every 10-15 minutes
        self.break_duration = (30, 90)  # Break for 30-90 seconds
        self.last_break_time = time.time()
        self.mouse_jitter = True  # Add small mouse movements
        self.session_limit = 0  # 0 = no limit, else minutes
        self.gradual_speed = True  # Gradually change speed
        
        # Statistics
        self.click_count = 0
        self.start_time = None
        
        # Game presets
        self.current_preset = "Custom"
        
        # Bind hotkeys by default
        self.bind_hotkeys()

    def load_preset(self, preset_name):
        """Load predefined game presets"""
        presets = {
            "Pet Sim 99 - Egg Hatching": {
                "base_delay": 0.05,
                "randomize_delay": True,
                "burst_mode": True,
                "burst_size": 3,
                "click_pattern": "area",
                "area_bounds": (900, 450, 1020, 550),
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            },
            "Blox Fruits - Mastery Farm": {
                "base_delay": 0.2,
                "randomize_delay": True,
                "burst_mode": True,
                "burst_size": 5,
                "click_pattern": "single",
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            },
            "Adopt Me - Pet Tasks": {
                "base_delay": 0.5,
                "randomize_delay": True,
                "burst_mode": False,
                "click_pattern": "single",
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            },
            "Tapping Legends - Max CPS": {
                "base_delay": 0.001,
                "randomize_delay": False,
                "burst_mode": True,
                "burst_size": 10,
                "click_pattern": "area",
                "area_bounds": (900, 400, 1020, 600),
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": False
            },
            "Bee Swarm - Pollen Collection": {
                "base_delay": 0.1,
                "randomize_delay": True,
                "burst_mode": False,
                "click_pattern": "circular",
                "circular_center": (960, 540),
                "circular_radius": 80,
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            },
            "Murder Mystery 2 - Combat": {
                "base_delay": 0.3,
                "randomize_delay": True,
                "burst_mode": True,
                "burst_size": 2,
                "click_pattern": "single",
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            },
            "Anime Fighting Sim - Training": {
                "base_delay": 0.15,
                "randomize_delay": True,
                "burst_mode": True,
                "burst_size": 4,
                "click_pattern": "area",
                "area_bounds": (850, 400, 1070, 650),
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            },
            "A Universal Time - Farming": {
                "base_delay": 0.25,
                "randomize_delay": True,
                "burst_mode": False,
                "click_pattern": "single",
                "mouse_button": "left",
                "roblox_only": True,
                "auto_breaks": True
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            for attr, value in preset.items():
                setattr(self, attr, value)
            self.current_preset = preset_name
            print(f"[INFO] Loaded preset: {preset_name}")

    def is_roblox_active(self):
        """Check if Roblox window is active"""
        if not self.roblox_only:
            return True
        try:
            active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            return "roblox" in active_window.lower() or "bloxstrap" in active_window.lower()
        except:
            return True  # Default to true if detection fails

    def should_take_break(self):
        """Check if it's time for an automatic break"""
        if not self.auto_breaks:
            return False
        
        time_since_break = time.time() - self.last_break_time
        break_threshold = random.uniform(self.break_interval[0], self.break_interval[1])
        return time_since_break > break_threshold

    def take_break(self):
        """Take an automatic break"""
        break_time = random.uniform(self.break_duration[0], self.break_duration[1])
        print(f"[INFO] Taking break for {int(break_time)} seconds...")
        time.sleep(break_time)
        self.last_break_time = time.time()

    def get_click_position(self):
        """Get position based on current click pattern"""
        if self.click_pattern == "single":
            if self.follow_mouse:
                return pyautogui.position()
            else:
                return self.fixed_position
                
        elif self.click_pattern == "area":
            x1, y1, x2, y2 = self.area_bounds
            x = random.randint(x1, x2)
            y = random.randint(y1, y2)
            return (x, y)
            
        elif self.click_pattern == "multi_point":
            return random.choice(self.multi_points)
            
        elif self.click_pattern == "circular":
            cx, cy = self.circular_center
            x = int(cx + self.circular_radius * math.cos(self.current_angle))
            y = int(cy + self.circular_radius * math.sin(self.current_angle))
            self.current_angle += 0.5  # Increment angle for next click
            if self.current_angle > 2 * math.pi:
                self.current_angle = 0
            return (x, y)
            
        return self.fixed_position

    def add_mouse_jitter(self):
        """Add small random mouse movements for humanization"""
        if self.mouse_jitter and random.random() < 0.1:  # 10% chance
            current_pos = pyautogui.position()
            jitter_x = random.randint(-5, 5)
            jitter_y = random.randint(-5, 5)
            new_x = max(0, min(current_pos[0] + jitter_x, pyautogui.size()[0]))
            new_y = max(0, min(current_pos[1] + jitter_y, pyautogui.size()[1]))
            pyautogui.moveTo(new_x, new_y, duration=0.1)

    def _calculate_delay(self):
        """Calculate delay with optional randomization and gradual speed changes"""
        delay = self.base_delay
        
        if self.randomize_delay:
            # Add ±30% randomization for more human-like behavior
            variation = delay * 0.3
            delay += random.uniform(-variation, variation)
            
        if self.gradual_speed and self.start_time:
            # Gradually change speed over time
            elapsed = time.time() - self.start_time
            speed_factor = 1 + 0.1 * math.sin(elapsed / 60)  # Sine wave over minutes
            delay *= speed_factor
            
        return max(0.001, delay)  # Ensure minimum delay

    def _click(self):
        """Main clicking loop with enhanced features"""
        clicks_done = 0
        self.start_time = time.time()
        self.click_count = 0
        self.last_break_time = time.time()
        
        print(f"[INFO] Started clicking with pattern: {self.click_pattern}")
        
        while self.running:
            # Check session limit
            if self.session_limit > 0:
                elapsed_minutes = (time.time() - self.start_time) / 60
                if elapsed_minutes > self.session_limit:
                    print(f"[INFO] Session limit reached ({self.session_limit} min)")
                    self.running = False
                    break
            
            # Check if Roblox is active
            if not self.is_roblox_active():
                time.sleep(1)
                continue
            
            # Check for automatic breaks
            if self.should_take_break():
                self.take_break()
                continue
            
            # Add occasional mouse jitter
            self.add_mouse_jitter()
            
            # Get click position based on pattern
            pos = self.get_click_position()
            
            if self.burst_mode:
                # Burst mode: multiple rapid clicks followed by delay
                for _ in range(self.burst_size):
                    if not self.running:
                        break
                    # Recalculate position for each click in area/circular modes
                    if self.click_pattern in ["area", "circular"]:
                        pos = self.get_click_position()
                    
                    for _ in range(self.click_type):
                        if self.is_roblox_active():
                            pyautogui.click(x=pos[0], y=pos[1], button=self.mouse_button)
                            self.click_count += 1
                        time.sleep(0.001)  # Minimal delay between multi-clicks
                    time.sleep(0.01)  # Small delay between burst clicks
                
                # Delay after burst
                time.sleep(self._calculate_delay())
            else:
                # Normal mode: single click with delay
                for _ in range(self.click_type):
                    if self.is_roblox_active():
                        pyautogui.click(x=pos[0], y=pos[1], button=self.mouse_button)
                        self.click_count += 1
                    time.sleep(0.001)  # Minimal delay between multi-clicks
                
                time.sleep(self._calculate_delay())

            clicks_done += 1
            if self.click_limit and clicks_done >= self.click_limit:
                self.running = False
                break

    def start_clicking(self):
        """Start the auto clicker"""
        if not self.running:
            self.running = True
            self._click_thread = threading.Thread(target=self._click, daemon=True)
            self._click_thread.start()
            print(f"[INFO] Auto clicker started with preset: {self.current_preset}")

    def stop_clicking(self):
        """Stop the auto clicker"""
        self.running = False
        print("[INFO] Auto clicker stopped.")

    def panic_stop(self):
        """Emergency stop - stops everything immediately"""
        self.running = False
        print("[PANIC] Emergency stop activated!")

    def toggle_clicking(self):
        """Toggle between start and stop"""
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def status(self):
        """Get current status and statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'running': self.running,
            'clicks': self.click_count,
            'elapsed': elapsed,
            'preset': self.current_preset,
            'roblox_active': self.is_roblox_active() if self.roblox_only else True
        }

    def bind_hotkeys(self):
        """Bind keyboard hotkeys"""
        if not self._hotkeys_bound:
            try:
                keyboard.add_hotkey(self.hotkey_start, self.toggle_clicking)
                keyboard.add_hotkey(self.hotkey_stop, self.stop_clicking)
                keyboard.add_hotkey(self.hotkey_panic, self.panic_stop)
                self._hotkeys_bound = True
                print(f"[INFO] Hotkeys bound: Start/Toggle({self.hotkey_start}), Stop({self.hotkey_stop}), Panic({self.hotkey_panic})")
            except Exception as e:
                print(f"[WARNING] Could not bind hotkeys: {e}")

    def unbind_hotkeys(self):
        """Unbind keyboard hotkeys"""
        if self._hotkeys_bound:
            try:
                keyboard.remove_hotkey(self.hotkey_start)
                keyboard.remove_hotkey(self.hotkey_stop)
                keyboard.remove_hotkey(self.hotkey_panic)
                self._hotkeys_bound = False
                print("[INFO] Hotkeys unbound.")
            except Exception as e:
                print(f"[WARNING] Could not unbind hotkeys: {e}")

    def safe_exit(self):
        """Safely exit the clicker"""
        self.stop_clicking()
        self.unbind_hotkeys()

if __name__ == "__main__":
    clicker = AutoClicker()
    
    # Load a preset for testing
    clicker.load_preset("Tapping Legends - Max CPS")

    print("[INFO] Auto clicker running. Press ESC to exit.")
    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        pass
    finally:
        clicker.safe_exit()