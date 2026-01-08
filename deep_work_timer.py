"""
Deep Work Timer with Face Detection
A focus timer that pauses when you're not present
"""

import customtkinter as ctk
import cv2
import threading
import time
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import sys
import os

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NotificationPopup:
    """Auto-dismissing notification popup"""
    def __init__(self, parent, message, duration=3000):
        self.popup = ctk.CTkToplevel(parent)
        self.popup.title("")
        self.popup.geometry("300x80")
        
        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (80 // 2)
        self.popup.geometry(f"300x80+{x}+{y}")
        
        # Always on top
        self.popup.attributes('-topmost', True)
        self.popup.overrideredirect(True)  # Remove window decorations
        
        # Modern styling
        frame = ctk.CTkFrame(self.popup, corner_radius=15, fg_color="#2b2b2b", border_width=2, border_color="#1f6aa5")
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        )
        label.pack(expand=True, pady=20)
        
        # Auto-dismiss after duration
        self.popup.after(duration, self.popup.destroy)


class TimerWindow:
    """Draggable, transparent timer display"""
    def __init__(self, parent, total_seconds):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Deep Work Timer")
        self.window.geometry("250x100")  # Increased width for seconds
        
        # Position at top-right corner
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"250x100+{screen_width-270}+20")  # Adjusted position
        
        # Window properties
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.9)
        self.window.overrideredirect(True)  # Remove title bar
        
        # Create main frame with border
        self.main_frame = ctk.CTkFrame(
            self.window,
            corner_radius=15,
            fg_color="#1a1a1a",
            border_width=3,
            border_color="#1f6aa5"
        )
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Timer label
        self.timer_label = ctk.CTkLabel(
            self.main_frame,
            text="00:00:00",
            font=("Segoe UI", 36, "bold"),
            text_color="#4CAF50"
        )
        self.timer_label.pack(expand=True)
        
        # Status indicator (small dot)
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="●",
            font=("Segoe UI", 12),
            text_color="#4CAF50"
        )
        self.status_label.pack(pady=(0, 5))
        
        # Dragging functionality
        self.x = 0
        self.y = 0
        self.main_frame.bind("<Button-1>", self.start_drag)
        self.main_frame.bind("<B1-Motion>", self.drag)
        self.timer_label.bind("<Button-1>", self.start_drag)
        self.timer_label.bind("<B1-Motion>", self.drag)
        
        # Timer state
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.is_paused = False
        self.is_running = True
        
        # Update timer display
        self.update_display()
        
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
        
    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    
    def update_display(self):
        """Update the timer display"""
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        self.timer_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update status indicator color
        if self.is_paused:
            self.status_label.configure(text_color="#FF9800")  # Orange when paused
            self.timer_label.configure(text_color="#FF9800")
        else:
            self.status_label.configure(text_color="#4CAF50")  # Green when running
            self.timer_label.configure(text_color="#4CAF50")
    
    def pause(self):
        """Pause the timer"""
        self.is_paused = True
        self.update_display()
    
    def resume(self):
        """Resume the timer"""
        self.is_paused = False
        self.update_display()
    
    def tick(self):
        """Decrease timer by one second if running"""
        if not self.is_paused and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()


class DeepWorkTimer:
    """Main application class"""
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Deep Work Timer")
        self.root.geometry("400x300")
        
        # Center window
        self.center_window(400, 300)
        
        # Variables
        self.timer_window = None
        self.face_cascade = None
        self.camera = None
        self.face_detection_thread = None
        self.timer_thread = None
        self.stop_threads = False
        self.face_detected = True
        self.no_face_start_time = None
        self.last_state = "running"
        
        # Development mode - set to False for final build
        self.show_webcam_preview = False
        
        # Load face detection model
        self.load_face_detector()
        
        # Create UI
        self.create_input_screen()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self, width, height):
        """Center window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_face_detector(self):
        """Load OpenCV face detection cascade"""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("Error: Could not load face detection model")
            sys.exit(1)
    
    def create_input_screen(self):
        """Create the initial input screen"""
        # Main frame
        frame = ctk.CTkFrame(self.root, corner_radius=20)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            frame,
            text="Deep Work Timer",
            font=("Segoe UI", 32, "bold"),
            text_color="#1f6aa5"
        )
        title.pack(pady=(30, 10))
        
        subtitle = ctk.CTkLabel(
            frame,
            text="Focus session with face detection",
            font=("Segoe UI", 14),
            text_color="#888888"
        )
        subtitle.pack(pady=(0, 30))
        
        # Input label
        input_label = ctk.CTkLabel(
            frame,
            text="Enter duration (minutes):",
            font=("Segoe UI", 16)
        )
        input_label.pack(pady=(10, 5))
        
        # Time input
        self.time_entry = ctk.CTkEntry(
            frame,
            width=200,
            height=50,
            font=("Segoe UI", 24),
            justify="center",
            placeholder_text="000"
        )
        self.time_entry.pack(pady=10)
        self.time_entry.focus()
        
        # Bind Enter key
        self.time_entry.bind("<Return>", lambda e: self.start_timer())
        
        # Start button
        start_btn = ctk.CTkButton(
            frame,
            text="Start Deep Work",
            width=200,
            height=50,
            font=("Segoe UI", 18, "bold"),
            command=self.start_timer,
            corner_radius=10,
            fg_color="#1f6aa5",
            hover_color="#1557a0"
        )
        start_btn.pack(pady=20)
        
    def start_timer(self):
        """Start the timer with entered duration"""
        try:
            minutes = int(self.time_entry.get())
            if minutes <= 0 or minutes > 999:
                self.show_error("Please enter a value between 1 and 999 minutes")
                return

            total_seconds = minutes * 60

            # Hide input window
            self.root.withdraw()

            # Create timer window
            self.timer_window = TimerWindow(self.root, total_seconds)

            # Start camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.show_error("Could not access webcam")
                return

            # Start face detection thread (only this runs in background)
            self.stop_threads = False
            self.face_detection_thread = threading.Thread(target=self.face_detection_loop, daemon=True)
            self.face_detection_thread.start()

            # Start timer in main thread (safe!)
            self.update_timer()  # This will self-schedule every second

        except ValueError:
            self.show_error("Please enter a valid number")


    def update_timer(self):
        """Main-thread timer update (safe for UI)"""
        if self.stop_threads or self.timer_window is None:
            return

        # Only tick if not paused
        if not self.timer_window.is_paused:
            self.timer_window.tick()  # This updates display safely (called from main thread)

        # Check if timer finished
        if self.timer_window.remaining_seconds <= 0:
            self.stop_threads = True
            self.show_completion()
        else:
            # Schedule next update in 1 second
            self.root.after(1000, self.update_timer)
    
    def show_error(self, message):
        """Show error dialog"""
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x150")
        
        # Center error window
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - 150
        y = (error_window.winfo_screenheight() // 2) - 75
        error_window.geometry(f"300x150+{x}+{y}")
        
        error_window.attributes('-topmost', True)
        
        label = ctk.CTkLabel(error_window, text=message, font=("Segoe UI", 14), wraplength=250)
        label.pack(expand=True, pady=20)
        
        btn = ctk.CTkButton(error_window, text="OK", command=error_window.destroy, width=100)
        btn.pack(pady=10)
    
    def face_detection_loop(self):
            """Background thread for face detection"""
            while not self.stop_threads:
                if self.camera is not None and self.camera.isOpened():
                    ret, frame = self.camera.read()
                    
                    if ret:
                        # Convert to grayscale
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Detect faces
                        faces = self.face_cascade.detectMultiScale(
                            gray,
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(30, 30)
                        )
                        
                        # Calculate confidence based on face detection
                        if len(faces) > 0:
                            # Face detected - calculate confidence based on size
                            largest_face = max(faces, key=lambda f: f[2] * f[3])
                            face_area = largest_face[2] * largest_face[3]
                            frame_area = frame.shape[0] * frame.shape[1]
                            
                            # Adjusted calculation for better sensitivity
                            confidence = min(100, (face_area / frame_area) * 1000)
                            
                            # Threshold (30 might be high if you sit far back; try 10 or 15 if it pauses too much)
                            face_present = confidence >= 30
                            
                            # Draw rectangle around face for preview
                            if self.show_webcam_preview:
                                x, y, w, h = largest_face
                                color = (0, 255, 0) if face_present else (0, 0, 255)
                                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                                cv2.putText(frame, f"Confidence: {confidence:.1f}%", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                        else:
                            face_present = False
                            if self.show_webcam_preview:
                                cv2.putText(frame, "No face detected", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # Show webcam preview (development mode)
                        if self.show_webcam_preview:
                            status_text = "RUNNING" if not self.timer_window.is_paused else "PAUSED"
                            status_color = (0, 255, 0) if not self.timer_window.is_paused else (0, 165, 255)
                            cv2.putText(frame, f"Status: {status_text}", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                            cv2.imshow("Webcam Preview (Development Mode)", frame)
                            # This waitKey handles the delay for preview mode
                            cv2.waitKey(1)
                        
                        # Handle face detection state changes
                        current_time = time.time()
                        
                        if not face_present:
                            if self.no_face_start_time is None:
                                self.no_face_start_time = current_time
                            elif current_time - self.no_face_start_time >= 5: # Wait 5 seconds before pausing
                                # No face for 5 seconds - pause
                                if not self.timer_window.is_paused:
                                    self.timer_window.pause()
                                    if self.last_state != "paused":
                                        # Use self.root.after to ensure UI updates happen on main thread
                                        self.root.after(0, lambda: NotificationPopup(self.root, "⏸️ Timer Paused\nFace not detected"))
                                        self.last_state = "paused"
                        else:
                            # Face detected
                            if self.no_face_start_time is not None:
                                self.no_face_start_time = None
                            
                            if self.timer_window.is_paused:
                                self.timer_window.resume()
                                if self.last_state != "running":
                                    self.root.after(0, lambda: NotificationPopup(self.root, "▶️ Timer Resumed\nWelcome back!"))
                                    self.last_state = "running"
                
                # Use a tiny sleep to prevent CPU hogging, but keep it fast (30ms approx 30FPS)
                if not self.show_webcam_preview:
                    time.sleep(0.5)
    
    
    def show_completion(self):
        """Show completion alert"""
        completion_window = ctk.CTkToplevel(self.root)
        completion_window.title("Deep Work Complete!")
        completion_window.geometry("400x200")
        
        # Center window
        completion_window.update_idletasks()
        x = (completion_window.winfo_screenwidth() // 2) - 200
        y = (completion_window.winfo_screenheight() // 2) - 100
        completion_window.geometry(f"400x200+{x}+{y}")
        
        completion_window.attributes('-topmost', True)
        
        # Congratulations message
        frame = ctk.CTkFrame(completion_window, corner_radius=20)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        emoji = ctk.CTkLabel(frame, text="🎉", font=("Segoe UI", 48))
        emoji.pack(pady=(20, 10))
        
        title = ctk.CTkLabel(
            frame,
            text="Deep Work Complete!",
            font=("Segoe UI", 24, "bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=5)
        
        message = ctk.CTkLabel(
            frame,
            text="Great focus session!",
            font=("Segoe UI", 14),
            text_color="#888888"
        )
        message.pack(pady=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            frame,
            text="Close",
            width=150,
            height=40,
            font=("Segoe UI", 14, "bold"),
            command=self.cleanup_and_exit,
            corner_radius=10
        )
        close_btn.pack(pady=15)
    
    def cleanup_and_exit(self):
        """Clean up resources and exit"""
        self.stop_threads = True
        
        # Release camera
        if self.camera is not None:
            self.camera.release()
        
        # Clear OpenCV cache
        cv2.destroyAllWindows()
        
        # Exit application
        self.root.quit()
        self.root.destroy()
        sys.exit(0)
    
    def on_closing(self):
        """Handle window close event"""
        # Only allow closing from input screen, not during timer
        if self.timer_window is None:
            self.cleanup_and_exit()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = DeepWorkTimer()
    app.run()