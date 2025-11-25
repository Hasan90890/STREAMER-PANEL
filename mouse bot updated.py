import tkinter as tk
from tkinter import ttk
import ctypes
import time
import threading
from ctypes import wintypes

class DarkAimAssistGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RENAULT BEBU")
        self.root.geometry("325x390")
        self.root.resizable(False, False)
        self.root.configure(bg='#1c1c1c')
        
        # Aim assist controller
        self.aim_assist = AimAssistController()
        
        # GUI variables
        self.strength_var = tk.DoubleVar(value=5.0)
        self.delay_var = tk.IntVar(value=100)
        self.hold_key_var = tk.StringVar(value="Mouse4")
        self.aim_assist.hold_key = 0x05
        self.current_mode = tk.StringVar(value="drag")  # 'drag' or 'recoil'
        
        self.setup_styles()
        self.setup_gui()
        self.start_aim_thread()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = '#1c1c1c'
        accent_color = '#4a4a4a'
        text_color = '#ffffff'
        highlight_color = '#3a3a3a'
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color, font=('Arial', 9))
        style.configure('Title.TLabel', background=bg_color, foreground=text_color, font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', background=bg_color, foreground='#cccccc', font=('Arial', 10))
        style.configure('TButton', background=accent_color, foreground=text_color,
                       font=('Arial', 9), focuscolor=style.configure(".")["background"])
        style.map('TButton', background=[('active', highlight_color)])
        style.configure('Green.TButton', background='#00b359', foreground='white')
        style.map('Green.TButton', background=[('active', '#00cc66')])
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Mode selection buttons (top bar)
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill='x', pady=(0, 10))
        
        self.drag_button = ttk.Button(mode_frame, text="Drag Assist", command=self.set_drag_mode, style='Green.TButton')
        self.drag_button.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        self.recoil_button = ttk.Button(mode_frame, text="Recoil Control", command=self.set_recoil_mode, style='TButton')
        self.recoil_button.pack(side='right', expand=True, fill='x', padx=(5, 0))
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(5, 15))
        
        title_label = ttk.Label(title_frame, text="RENAULT BEBU", style='Title.TLabel')
        title_label.pack()
        subtitle_label = ttk.Label(title_frame, text="Professional Aim Assist", style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill='x', pady=(0, 15))
        
        status_content = ttk.Frame(status_frame)
        status_content.pack(fill='x')
        
        ttk.Label(status_content, text="Hold Key:").grid(row=0, column=0, sticky='w')
        ttk.Label(status_content, textvariable=self.hold_key_var, 
                 foreground='#00a8ff', font=('Arial', 9, 'bold')).grid(row=0, column=1, sticky='w', padx=(5, 0))
        
        self.key_button = ttk.Button(status_content, text="Change Key", command=self.start_key_binding, width=12)
        self.key_button.grid(row=0, column=2, padx=(20, 0))
        
        ttk.Label(status_content, text="Assist Status:").grid(row=1, column=0, sticky='w', pady=(8, 0))
        self.status_label = ttk.Label(status_content, text="INACTIVE", foreground='#ff4444', font=('Arial', 9, 'bold'))
        self.status_label.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=(8, 0))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Strength setting
        strength_frame = ttk.Frame(settings_frame)
        strength_frame.pack(fill='x', pady=5)
        
        ttk.Label(strength_frame, text="Strength:").pack(side='left')
        self.strength_value = ttk.Label(strength_frame, text="5.0", foreground='#00a8ff')
        self.strength_value.pack(side='right')
        
        strength_scale = ttk.Scale(strength_frame, from_=0.1, to=9.0, 
                                  variable=self.strength_var, orient='horizontal',
                                  command=self.on_strength_change)
        strength_scale.pack(fill='x', pady=5)
        
        # Delay setting
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill='x', pady=5)
        
        ttk.Label(delay_frame, text="Delay (ms):").pack(side='left')
        self.delay_value = ttk.Label(delay_frame, text="100", foreground='#00a8ff')
        self.delay_value.pack(side='right')
        
        delay_scale = ttk.Scale(delay_frame, from_=0, to=1000, 
                               variable=self.delay_var, orient='horizontal',
                               command=self.on_delay_change)
        delay_scale.pack(fill='x', pady=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding=10)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats_content = ttk.Frame(stats_frame)
        stats_content.pack(fill='x')
        
        ttk.Label(stats_content, text="Compensations:").pack(side='left')
        self.stats_count = ttk.Label(stats_content, text="0", foreground='#00ff88', font=('Arial', 9, 'bold'))
        self.stats_count.pack(side='left', padx=(5, 0))
        
        ttk.Button(stats_content, text="Reset", command=self.reset_counter).pack(side='right')
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Hide Window", command=self.hide_window).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side='right')
    
    def set_drag_mode(self):
        """Activate upward mouse movement."""
        self.current_mode.set("drag")
        self.drag_button.configure(style='Green.TButton')
        self.recoil_button.configure(style='TButton')
        self.aim_assist.mode = "drag"
    
    def set_recoil_mode(self):
        """Activate downward mouse movement."""
        self.current_mode.set("recoil")
        self.drag_button.configure(style='TButton')
        self.recoil_button.configure(style='Green.TButton')
        self.aim_assist.mode = "recoil"
    
    def on_strength_change(self, value):
        strength = float(value)
        self.strength_value.config(text=f"{strength:.1f}")
        self.aim_assist.strength = strength
        
    def on_delay_change(self, value):
        delay = int(float(value))
        self.delay_value.config(text=f"{delay}")
        self.aim_assist.activation_delay = delay
        
    def reset_counter(self):
        self.aim_assist.compensation_count = 0
        self.stats_count.config(text="0")
        
    def start_key_binding(self):
        self.key_button.config(text="Press any key...")
        self.key_binding_active = True
        self.root.after(100, self.check_key_binding)
        
    def check_key_binding(self):
        if self.key_binding_active:
            for key_code in range(1, 256):
                if self.aim_assist.get_async_key_state(key_code):
                    # Block invalid or unwanted keys
                    if key_code in (0x01, 0x02, 0x04, 0xE7, 0xFF):
                        self.key_button.config(text="Invalid key!")
                        self.root.after(1000, lambda: self.key_button.config(text="Change Key"))
                        self.key_binding_active = False
                        return
                    
                    # Accept valid key
                    self.aim_assist.hold_key = key_code
                    key_name = self.get_key_name(key_code)
                    self.hold_key_var.set(key_name)
                    self.key_button.config(text="Change Key")
                    self.key_binding_active = False
                    return
            self.root.after(50, self.check_key_binding)

    
    def hide_window(self):
        self.root.withdraw()
        self.root.after(5000, self.show_window)
    
    def show_window(self):
        self.root.deiconify()
    
    def update_display(self):
        if self.aim_assist.is_active:
            self.status_label.config(text="ACTIVE", foreground='#00ff88')
        else:
            self.status_label.config(text="INACTIVE", foreground='#ff4444')
        self.stats_count.config(text=str(self.aim_assist.compensation_count))
    
    def get_key_name(self, key_code):
        key_names = {
            0x02: "RMB", 0x04: "MMB", 0x05: "Mouse4", 0x06: "Mouse5",
            0x10: "Shift", 0x11: "Ctrl", 0x12: "Alt", 0x14: "Caps",
            0x20: "Space", 0x21: "PgUp", 0x22: "PgDn", 0x23: "End",
            0x24: "Home", 0x25: "Left", 0x26: "Up", 0x27: "Right",
            0x28: "Down", 0x41: "A", 0x42: "B", 0x43: "C", 0x44: "D"
        }
        return key_names.get(key_code, f"Key0x{key_code:02X}")
    
    def start_aim_thread(self):
        def aim_loop():
            while True:
                self.aim_assist.update()
                self.root.after(10, self.update_display)
                time.sleep(0.01)
        threading.Thread(target=aim_loop, daemon=True).start()


class AimAssistController:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.strength = 5.0
        self.RECOIL_COMPENSATION = -1.5
        self.hold_key = 0x05
        self.activation_delay = 100
        self.is_active = False
        self.is_aiming = False
        self.mouse_hold_timer = 0
        self.compensation_count = 0
        self.hold_key_pressed = False
        self.mode = "drag"  # drag = upward, recoil = downward
        
        self.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.user32.GetAsyncKeyState.restype = ctypes.c_short
        self.user32.mouse_event.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p]
    
    def get_async_key_state(self, vKey):
        return self.user32.GetAsyncKeyState(vKey) & 0x8000 != 0
    
    def mouse_event(self, dwFlags, dx, dy, dwData=0):
        self.user32.mouse_event(dwFlags, dx, dy, dwData, 0)
    
    def update(self):
        current_time = time.time() * 1000
        hold_key_pressed = self.get_async_key_state(self.hold_key)
        
        if hold_key_pressed and not self.hold_key_pressed:
            self.hold_key_pressed = True
            self.is_active = True
        elif not hold_key_pressed and self.hold_key_pressed:
            self.hold_key_pressed = False
            self.is_active = False
            self.is_aiming = False
            self.mouse_hold_timer = 0
        
        if self.is_active and self.get_async_key_state(0x01):
            if not self.is_aiming:
                if self.mouse_hold_timer == 0:
                    self.mouse_hold_timer = current_time
                elif current_time - self.mouse_hold_timer >= self.activation_delay:
                    self.is_aiming = True
                    self.mouse_hold_timer = current_time
            else:
                current_strength = self.strength
                if current_time - self.mouse_hold_timer >= 600:
                    current_strength *= 0.2
                
                # Move depending on mode
                move_value = int(self.RECOIL_COMPENSATION * current_strength)
                if self.mode == "drag":
                    self.mouse_event(0x0001, 0, move_value)
                elif self.mode == "recoil":
                    self.mouse_event(0x0001, 0, -move_value)
                self.compensation_count += 1
        else:
            if self.is_active:
                self.mouse_hold_timer = current_time if self.get_async_key_state(0x01) else 0
            self.is_aiming = False


def main():
    root = tk.Tk()
    app = DarkAimAssistGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
n()
