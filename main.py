import serial
import time
import subprocess
import threading

from flask import Flask, render_template, Response
import json


# ============================================================
# CONFIGURATION
# ============================================================

SERIAL_PORT = "/dev/cu.usbmodemB0818497DA102"
BAUD_RATE = 9600

WHale_DISTANCE_THRESHOLD = 10

captain = "+13105677102"
message = "WHALE DETECTED! Motor has been stopped."

MP3_FILE = "test.mp3"


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


# Shared dashboard state
dashboard = {
    "distance": None,
    "motorStopping": False,
    "messageSent": False,
    "whaleDetected": False
}


# ============================================================
# ARDUINO
# ============================================================

arduino = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)

# Arduino often resets when the serial connection opens
time.sleep(2)

# Throw away old serial data
arduino.reset_input_buffer()


# ============================================================
# DASHBOARD ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/events")
def events():

    def generate():

        while True:

            data = json.dumps(dashboard)

            yield f"data: {data}\n\n"

            time.sleep(0.2)

    return Response(
        generate(),
        mimetype="text/event-stream"
    )


# ============================================================
# WHALE DETECTION
# ============================================================

def whale_detector():

    while True:

        line = arduino.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        # Ignore empty serial lines
        if not line:
            continue

        # Try to convert Arduino value to a number
        try:
            distance = float(line)

        except ValueError:
            print(f"Invalid Arduino data: {line!r}")
            continue

        print(f"Distance: {distance:.2f} cm")

        # Update dashboard
        dashboard["distance"] = distance


        # ====================================================
        # WHALE DETECTED
        # ====================================================

        if distance < WHale_DISTANCE_THRESHOLD:

            # Don't repeatedly trigger the whale detection
            if not dashboard["whaleDetected"]:

                dashboard["whaleDetected"] = True
                dashboard["motorStopping"] = True

                print("WHALE DETECTED")

                # ------------------------------------------------
                # STOP MOTOR
                # ------------------------------------------------

                print("Sending STOP to Arduino")

                arduino.write(b"STOP\n")
                arduino.flush()

                print("STOP sent")


                # ------------------------------------------------
                # SEND iMESSAGE
                # ------------------------------------------------

                try:

                    script = f'''
                    tell application "Messages"
                        set targetService to 1st service whose service type = iMessage
                        set targetBuddy to buddy "{captain}" of targetService
                        send "{message}" to targetBuddy
                    end tell
                    '''

                    subprocess.run(
                        ["osascript", "-e", script],
                        check=True
                    )

                    dashboard["messageSent"] = True

                    print("Text message sent")

                except subprocess.CalledProcessError as e:

                    print("Could not send text:", e)

                    dashboard["messageSent"] = False


                # ------------------------------------------------
                # PLAY AUDIO
                # ------------------------------------------------

                print("Playing whale alert")

                subprocess.run([
                    "afplay",
                    MP3_FILE
                ])

                print("Audio finished")


        # ====================================================
        # NO WHALE
        # ====================================================

        else:

            # Only send START if we haven't detected a whale
            if not dashboard["whaleDetected"]:

                dashboard["motorStopping"] = False

                print("Sending START to Arduino")

                arduino.write(b"START\n")
                arduino.flush()


# ============================================================
# START ARDUINO THREAD
# ============================================================

arduino_thread = threading.Thread(
    target=whale_detector,
    daemon=True
)

arduino_thread.start()


# ============================================================
# START WEB SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("====================================")
    print("🐋 Whale Detector Dashboard")
    print("====================================")
    print()
    print("Open:")
    print("http://localhost:5000")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
