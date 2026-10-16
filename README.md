<img width="3900" height="1300" alt="QuantumBlink Logo" src="https://github.com/user-attachments/assets/960beb12-e78d-4fcb-94af-f36e85073cd9" />


# QuantumBlink

**This mod requires a webcam to use. All video is processed on your computer and is never saved or sent anywhere. The mod's webcam program only tells the game whether your eyes are open or closed.**

QuantumBlink lets you interact with quantum objects by closing your eyes. It watches your webcam for blinks and allows quantum objects to move the moment you do, simulating how the quantum mechanics should work.

## Features

- Move quantum objects through eye tracked blinking via a webcam.
- Two blink modes to accommodate different setups.

## Requirements

- Outer Wilds on a Windows PC
- A webcam that can see your face. Good lighting on your face helps.

## Installation

1. Install QuantumBlink from the [Outer Wilds Mod Manager](https://outerwildsmods.com/mod-manager/).
2. Start the game. The webcam starts by itself in the background.
3. To check it's working, go to **Options > MODS > QuantumBlink > CALIBRATION** and blink. The eyes on the screen close each time a blink counts.
4. Calibrate if needed.

## Webcam placement

- **Best:** to the left or right of your monitor, at eye level. A webcam level with your eyes will give you the most accurate blink reading.
- Also works: on top of your monitor, may experience unintentional blinks by looking at the bottom of your monitor

## Settings

Find these in **Options > MODS > QuantumBlink**.

**Settings tab**

- **Blink mode:** In **Real-time** mode, every blink counts the moment it happens. In **Intentional** mode, a blink only counts when you keep your eyes closed for a moment, so normal blinking doesn't affect the game. Use Intentional if quantum objects move as you open your eyes.
- **Debug logging:** Logs every blink and every quantum move to the mod console.

**Calibration tab**

- **Blink sensitivity:** Increase it if your blinks get missed. Decrease it if blinks count when you didn't blink. Changes apply right away, so you can test them on the spot.
- **Intentional hold time:** How long you must keep your eyes closed in Intentional mode. Only shown in Intentional mode.
- **Webcam number:** Which webcam to use. 1 is your default webcam.
- **Restart webcam:** Starts the webcam again if it stopped, or after closing another program that was using it.

## Privacy

Your webcam video is processed on your computer and is never saved or sent anywhere. The mod's webcam program only tells the game whether your eyes are open or closed.

## Known limitations

- Windows only.
- Can't be used together with QuantumBlinkVR. Use one or the other.
- Not yet tested together with other mods that change quantum objects, such as Quantum Space Buddies.
- The download is larger than most mods, because the webcam program includes its own copy of Python and MediaPipe.

## Troubleshooting

The **CALIBRATION** tab tells you what's wrong:

- **"Can't see your face":** Check your lighting, and that your face is in the webcam's view.
- **"Couldn't open webcam":** Another program may be using the webcam (like Discord, OBS or a browser). Close it and press **Restart webcam**. If you have more than one webcam, try another **Webcam number**.
- **"Can't find the webcam companion":** Some antivirus programs wrongly flag the webcam program and remove it. Restore `BlinkCompanion.exe` from your antivirus's quarantine and allow it, then reinstall the mod.

The webcam program writes a log to `BlinkCompanion\BlinkCompanion.log` in the mod's folder, which helps when reporting a problem.

## Future plans

- Testing with Quantum Space Buddies and other mods that change quantum objects

## Credits

- Mod by **Zra**
- [MediaPipe](https://github.com/google-ai-edge/mediapipe) by Google, tracks your face and eyes, including its Face Landmarker model
- [OpenCV](https://opencv.org/), which reads the webcam
- [OWML](https://owml.outerwildsmods.com/) and the Outer Wilds modding community
- Outer Wilds by Mobius Digital

## License

The mod's own code is released under the MIT license. The webcam program includes MediaPipe, OpenCV and Python, which each remain under their own open-source licenses. This mod is free and non-commercial.
