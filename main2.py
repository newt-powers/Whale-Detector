from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os
import subprocess
import serial
import time

load_dotenv()

#arduino-python serial transfer
# arduino = serial.Serial("/dev/cu.usbserial-B0818497DA102", 9600, timeout=1)
arduino = serial.Serial("/dev/cu.usbmodemB0818497DA102", 9600, timeout=1)
time.sleep(2)
stop_flag = False
whale_detected = False

#eleven labs setup
message = "Whale detected. The ship is slowing down."
captain = "+13105677102"

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

audio = elevenlabs.text_to_speech.convert(
    text = message,
    voice_id = "JBFqnCBsd6RMkjVDRZzb",
    model_id = "eleven_v3",
    output_format="mp3_44100_128",
)

subprocess.run(["afplay", "test.mp3"])


# play(audio)

# with open("test.mp3", "wb") as f:
#     for chunk in audio:
#         f.write(chunk)

# print("Audio saved to test.mp3")

#number of repeats before whale detected is true
# i = 0

#while loop to repeat checking process
while True:
    line = arduino.readline().decode("utf-8").strip()
    time.sleep(2)

    if not line:
        continue

    try:
        distance = float(line)
    except ValueError:
        print(f"Invalid Arduino data: {line!r}")
        continue

    # if line:
    print(f"Distance: {distance:.2f} cm")

    # print(f"Loop: {i}")
    if distance < 10:
        whale_detected = True
    
    if whale_detected == True:
        print("WHALE DETECTED")
        print("Sending STOP to Arduino")
        arduino.write(b"STOP\n")
        arduino.flush() #???
        print("STOP sent")
        # Send iMessage
        script = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "{captain}" of targetService
            send "{message}" to targetBuddy
        end tell
        '''
        subprocess.run(["osascript", "-e", script])

        #play eleven labs generated audio
        print("Playing audio")
        subprocess.run(["afplay", "test.mp3"])
        # time.sleep(5) #ensure the audio can play???
        break
    else:
        # print("Sending START to Arduino")
        arduino.write(b"START\n")
        arduino.flush()
        # i += 1
