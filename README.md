
# Hand Gesture Based Mouse and Keyboard Control

This Python program uses hand gestures, detected through color tape markers, to control a computer’s mouse and keyboard. The system recognizes three color tapes (yellow, blue, and red) placed on specific fingers. The program uses the OpenCV library for video capture, color detection, and gesture recognition, and PyAutoGUI for simulating mouse and keyboard events.

## Requirements

- Python 3.x
- OpenCV (`cv2`)
- Numpy
- PyAutoGUI
- A webcam for detecting gestures

## Color Tapes Setup

- **Yellow Tape**: Placed on the **right index finger**.
- **Blue Tape**: Placed on the **left middle finger**.
- **Red Tape**: Placed on the **left index finger**.

## How It Works

### 1. **Color Detection**

The program uses OpenCV to detect colors in the live video feed from the webcam. The colors of the tapes are detected in the HSV (Hue, Saturation, Value) color space. The following color ranges are used:

- **Yellow**: `np.array([[20, 100, 100], [30, 255, 255]])`
- **Blue**: `np.array([[100, 150, 0], [120, 255, 255]])`
- **Red**: `np.array([[170, 120, 70], [180, 255, 255]])`

### 2. **Mask Creation and Contour Detection**

- For each color, a mask is created to filter out the regions matching the color.
- The mask undergoes morphological operations (erosion and dilation) to remove noise and enhance the detection of solid colored regions.
- The program then calculates the centroid of the largest contour within the filtered mask. This is used to track the position of the finger with the color tape.

### 3. **Cursor and Action Control**

Based on the relative positions of the centroids of the yellow, blue, and red regions, the program determines whether to move the cursor, perform a left or right click, scroll, or perform other keyboard actions.

- **Yellow (Right Index Finger)**: Controls the cursor position.
- **Red (Left Index Finger)**: Triggers left click.
- **Blue (Left Middle Finger)**: Triggers right click or other keyboard actions.

### 4. **Modes and Controls**

The program has three modes, which are controlled by keypresses:

- **Mouse Mode**: Toggles mouse control on or off.
  - **Press `P`** to toggle Mouse Mode.
- **Keyboard Mode**: Toggles keyboard control on or off.
  - **Press `A`** to toggle Keyboard Mode.
- **Keyboard 1 Mode**: A secondary keyboard control mode.
  - **Press `B`** to toggle Keyboard 1 Mode.

The program supports actions like:

- **Mouse Move**: Move the cursor based on the yellow tape.
- **Click**: Left or right click based on the proximity of the blue and red tapes.
- **Scroll**: Scroll up or down.
- **Keyboard Actions**: Perform keyboard shortcuts, such as volume control, copy-paste, and screen capture.

### 5. **Main Loop**

In the main loop:
- The webcam captures the video feed.
- The hand gestures are detected and processed.
- The status of control modes is checked (Mouse, Keyboard, Keyboard 1).
- The appropriate actions (mouse movement, clicks, scroll, or keyboard actions) are performed based on the detected gestures.

### Key Presses for Control

- **C**: Toggle centroids display.
- **P**: Turn on/off Mouse Mode.
- **A**: Turn on/off Keyboard Mode.
- **B**: Turn on/off Keyboard 1 Mode.
- **ESC**: Exit the program.

## Conclusion

This hand gesture-based control system allows users to interact with their computers using simple hand movements. By placing colored tape on specific fingers, the system can detect gestures to control the mouse, click, scroll, and even perform keyboard actions. For project guide, please download **'Project Report.pdf'**

