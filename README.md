# FocusGuard
A modern, minimalist timer application that uses your webcam to detect when you're present and automatically pauses when you step away. Maximize focus. Eliminate distractions. Keep glued to your screen, eh? 
## Features

   - ✨ **Smart Face Detection** - Pauses automatically when you're not at your desk
   - 🎯 **Distraction-Free** - Transparent, always-on-top timer that stays out of your way
   - ⏱️ **Flexible Duration** - Set timers from 1 to 999 minutes
   - 🎨 **Modern UI** - Clean, professional interface with CustomTkinter
   - 🔔 **Smart Notifications** - Auto-dismissing alerts for pause/resume events
   - 📍 **Draggable Timer** - Position the timer wherever you want on screen

## Requirements

- Windows 11 (also works on Windows 10)
- Python 3.8 or higher
- Webcam

## Installation & Setup

### Option 1: Run from Source (For Development)

1. **Install Python** (if not already installed)
   - Download from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python deep_work_timer.py
   ```

### Option 2: Build Windows EXE (Recommended for Daily Use)

1. **Install Dependencies** (if not done already)
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the EXE**
   ```bash
   pyinstaller --onefile --windowed --name="DeepWorkTimer" --icon=NONE deep_work_timer.py
   ```

3. **Find Your EXE**
   - The executable will be in the `dist` folder
   - File name: `DeepWorkTimer.exe`
   - You can move this file anywhere and double-click to run

## How to Use

1. **Launch the App**
   - Double-click `DeepWorkTimer.exe` (or run `python deep_work_timer.py`)

2. **Set Your Timer**
   - Enter the duration in minutes (e.g., 90 for a 90-minute session)
   - Press Enter or click "Start Deep Work"

3. **Focus on Your Work**
   - The timer appears in the top-right corner
   - Green = Running, Orange = Paused
   - Timer is draggable - position it wherever you like

4. **Automatic Pause/Resume**
   - Timer pauses if you're away for 5+ seconds
   - Automatically resumes when you return
   - Small notifications appear for 3 seconds

5. **Completion**
   - When time expires, you'll see a completion alert
   - Click "Close" to exit the application

## Technical Details

### Face Detection Logic
- Checks for your face every 5 seconds (to save CPU)
- Requires face confidence > 30% to continue timer
- Tolerates brief head turns and movements
- 5-second grace period before pausing

### Timer Display
- Format: HH:MM (hours:minutes)
- Size: 200x100 pixels
- Transparent background with colored border
- Always stays on top of other windows

### Performance
- Low CPU usage (checks every 5 seconds, not continuously)
- Webcam runs silently in background
- Cache automatically cleared on exit

## Troubleshooting

### "Could not access webcam" Error
- Check if another app is using your webcam
- Grant camera permissions in Windows Settings
- Try restarting your computer

### Timer Not Pausing
- Ensure good lighting in your room
- Face the camera directly during checks
- Adjust your sitting position if needed

### App Won't Start
- Make sure all dependencies are installed
- Try running as administrator
- Check Windows Defender hasn't blocked it

### Build Issues with PyInstaller
If you get errors during build, try:
```bash
# Alternative build command with more compatibility
pyinstaller --onefile --windowed --name="DeepWorkTimer" --add-data "C:\Python3X\Lib\site-packages\customtkinter;customtkinter" deep_work_timer.py
```

Replace `C:\Python3X` with your actual Python installation path.

## File Structure

```
deep-work-timer/
│
├── deep_work_timer.py       # Main application code
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
└── dist/                     # Created after building
    └── DeepWorkTimer.exe     # Your executable file
```

## Dependencies

- **customtkinter** - Modern, customizable UI framework
- **opencv-python** - Webcam access and face detection
- **Pillow** - Image processing support
- **pyinstaller** - For building the .exe file

## Privacy & Security

- ✅ All processing happens locally on your computer
- ✅ No data is sent to any server
- ✅ Webcam feed is never recorded or saved
- ✅ Cache is cleared when you exit the app

## Tips for Best Results

1. **Lighting**: Ensure your face is well-lit
2. **Position**: Sit facing the camera
3. **Distance**: Stay within 2-3 feet of your webcam
4. **Environment**: Minimize movement in the background
5. **Focus**: The 5-second check interval means you can briefly look away

## Customization

Want to adjust settings? Edit these variables in `deep_work_timer.py`:

```python
# Line ~272: Face detection interval
time.sleep(5)  # Change 5 to check more/less frequently

# Line ~212: Pause delay
elif current_time - self.no_face_start_time >= 5:  # Change delay time

# Line ~229: Face confidence threshold
face_present = confidence >= 30  # Adjust sensitivity (0-100)

# Line ~14: Notification duration
NotificationPopup(self.root, message, duration=3000)  # milliseconds
```

## Known Limitations

- Timer can only be closed when it expires (by design)
- Requires adequate lighting for face detection
- One face per session (doesn't handle multiple people)
- Windows only (Linux/Mac would need modifications)

## Future Enhancements

Potential features for future versions:
- Statistics tracking (sessions completed, total focus time)
- Customizable themes and colors
- Sound notifications (optional)
- Keyboard shortcuts
- Multi-monitor support
- Settings panel

## License

This is a personal productivity tool. Feel free to modify and use as needed.



---

**Built for focused, distraction-free deep work sessions. Happy focusing! 🎯**
