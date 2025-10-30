#!/usr/bin/env python

import subprocess
import argparse
import time
import os
import re
import sys
from datetime import datetime, timedelta

# Default dimensions just in case
DEFAULT_HEIGHT = 24
DEFAULT_WIDTH = 80


# Parameter validation functions
def hhmm_type(s: str) -> str:
    _TIME_RE = re.compile(r"^(?P<hour>[0-9]{2}):(?P<min>[0-9]{2})$")
    m = _TIME_RE.match(s)
    if not m:
        raise argparse.ArgumentTypeError(f"invalid time: '{s}' (expected format HH:MM)")

    h = int(m.group("hour"))
    mnt = int(m.group("min"))

    if h < 0 or h > 23:
        raise argparse.ArgumentTypeError(
            f"hour out of range: {h:02d} (expected 00..23)"
        )
    if mnt < 0 or mnt > 59:
        raise argparse.ArgumentTypeError(
            f"minute out of range: {mnt:02d} (expected 00..59)"
        )

    # return normalized zero-padded string (keeps exact HH:MM shape)
    return f"{h:02d}:{mnt:02d}"


def timeTargetToSeconds(timetarget):
    if re.match(r"^\d{2}:\d{2}$", timetarget):
        hour, minute = map(int, timetarget.split(":"))
        today = datetime.now()
        end_time = today.replace(hour=hour, minute=minute, second=0)
        if end_time <= today:
            end_time += timedelta(days=1)
    else:
        end_time = datetime.strptime(timetarget, "%Y-%m-%d %H:%M:%S")
    return (end_time - datetime.now()).total_seconds()


# Arguments
parser = argparse.ArgumentParser(description="Fancy countdown script")

parser.add_argument(
    "-f",
    "--font",
    action="store",
    help="Custom font file",
    default=os.path.join(os.getcwd(), "font.txt"),
)
parser.add_argument(
    "-n", "--nocenter", action="store_true", help="Do not center timer (more efficient)"
)

parser.add_argument(
    "timetarget", help="Time target. Must be in HH:MM format.", type=hhmm_type
)

args = parser.parse_args()

centered = not args.nocenter
fontFile = args.font
timetarget = args.timetarget
seconds = timeTargetToSeconds(timetarget)


# Turn string into blocky ascii representation
# Supports 0-9, colon
def asciiFormat(string1, string2, font):
    # enumerate numbers and colons
    string1 = list(map(int, [c.replace(":", "10") for c in list(string1)]))
    string2 = list(map(int, [c.replace(":", "10") for c in list(string2)]))
    height = len(font[0])

    frame = ""
    # fill frame top to bottom
    for i in range(height):
        for char in string1[:-1]:
            frame += font[char][i] + " "
        frame += font[string1[-1]][i]
        frame += "\n"
    for i in range(2):
        frame += "\n"
    for i in range(height):
        for char in string2[:-1]:
            frame += font[char][i] + " "
        frame += font[string2[-1]][i]
        frame += "\n"
    return frame[:-1]


# Pad with spaces and newlines to center
def center(frame, termDimensions):
    if centered:
        termHeight = termDimensions[0]
        termWidth = termDimensions[1]
        frame = frame.split("\n")
        frameWidth = max(map(len, frame))
        frameHeight = len(frame)
        # pad horizontally
        pad = " " * int((termWidth - frameWidth) / 2)
        frame = "\n".join([(pad + line + pad) for line in frame])

        # pad vertically
        pad = "\n" * int((termHeight - frameHeight) / 2)
        frame = pad + frame + pad
    clear()
    return frame


# Clear screen
def clear():
    # no idea how this works but it does
    print("\033c")


# Terminal dimensions [height, width]
def getTermDimensions():
    try:
        dimensions = subprocess.check_output(["stty", "size"]).split()
        return list(map(int, dimensions))
    except subprocess.CalledProcessError:
        return [DEFAULT_HEIGHT, DEFAULT_WIDTH]


def exit():
    sys.exit(0)


if __name__ == "__main__":
    # Load font file
    with open(fontFile, "r") as f:
        font = f.read().split("\n<---->\n")
        font = [symbol.split("\n") for symbol in font]

    # Countdown
    while seconds >= 0:
        try:
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            t1 = "00:00:00"
            t2 = "%02d:%02d:%02d" % (h, m, s)
            print(center(asciiFormat(t1, t2, font), getTermDimensions()), end="")
            seconds -= 1
            time.sleep(1)
        except KeyboardInterrupt:
            exit()
