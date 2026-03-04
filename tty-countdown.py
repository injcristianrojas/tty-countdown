#!/usr/bin/env python

import argparse
import time
import re
import sys
import shutil
from datetime import datetime, timedelta
from glyphs import numbers
from functions.countdown import get_times

font = numbers.font


def hhmm_type(s: str) -> datetime:
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
    target = datetime.strptime(f"{h:02d}:{mnt:02d}", "%H:%M").time()
    now = datetime.now()
    dt = datetime.combine(now.date(), target)
    if dt <= now:
        dt += timedelta(days=1)
    return dt


def timeTargetToSeconds(timetarget):
    return (timetarget - datetime.now()).total_seconds()


parser = argparse.ArgumentParser(description="Fancy countdown script")
parser.add_argument(
    "timetarget", help="Time target. Must be in HH:MM format.", type=hhmm_type
)

args = parser.parse_args()
timetarget = args.timetarget
timetarget_string = timetarget.strftime("%H:%M")
seconds = timeTargetToSeconds(timetarget)


def asciiFormat(string1, string2):
    string1 = list(map(int, [c.replace(":", "10") for c in list(string1)]))
    string2 = list(map(int, [c.replace(":", "10") for c in list(string2)]))
    height = len(font[0])

    frame = ""
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
    for i in range(2):
        frame += "\n"
    frame += "              Countdown ends at {}\n".format(timetarget_string)
    return frame[:-1]


def center(frame):
    terminal_size = shutil.get_terminal_size()
    (termHeight, termWidth) = (terminal_size.lines, terminal_size.columns)
    frame = frame.split("\n")
    frameWidth = max(map(len, frame))
    frameHeight = len(frame)
    pad = " " * int((termWidth - frameWidth) / 2)
    frame = "\n".join([(pad + line + pad) for line in frame])
    pad = "\n" * int((termHeight - frameHeight) / 2)
    frame = pad + frame + pad
    print("\033c")
    return frame


def exit():
    sys.exit(0)


if __name__ == "__main__":
    while True:
        try:
            t1, t2 = get_times(timetarget_string)
            print(center(asciiFormat(t1, t2)), end="")
            seconds -= 1
            time.sleep(1)
        except KeyboardInterrupt:
            exit()
