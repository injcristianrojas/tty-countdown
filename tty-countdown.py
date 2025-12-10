#!/usr/bin/env python

import argparse
import time
import re
import sys
import shutil
from datetime import datetime, timedelta
from glyphs import numbers

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


def get_times(seconds):
    now = datetime.now().replace(microsecond=500000)
    end_time = now + timedelta(seconds=seconds)
    current_time = now.strftime("%H:%M:%S")
    time_left = end_time - now
    if time_left.total_seconds() <= 0:
        remaining_time = "00:00:00"
    else:
        total_hours = time_left.total_seconds() / 3600
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        seconds = int(((total_hours - hours) * 60 - minutes) * 60)
        if seconds >= 60:
            seconds = 0
        remaining_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return current_time, remaining_time


def wait_until_next_second():
    now = time.time()
    next_second = int(now) + 1
    sleep_time = next_second - now
    print(
        "Syncing... waiting {0:.2f} seconds until the next second in time... ".format(
            sleep_time
        ),
        end="",
    )
    time.sleep(sleep_time)
    print("Launching timer.")


def exit():
    sys.exit(0)


if __name__ == "__main__":
    wait_until_next_second()
    while True:
        try:
            t1, t2 = get_times(seconds)
            print(center(asciiFormat(t1, t2)), end="")
            seconds -= 1
            time.sleep(1)
        except KeyboardInterrupt:
            exit()
