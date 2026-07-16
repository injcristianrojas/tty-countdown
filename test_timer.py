import time

from functions.countdown import get_times

if __name__ == "__main__":
    while True:
        t1, t2 = get_times("20:37")
        print(f"Current time : {t1}")
        print(f"Time left    : {t2}")
        time.sleep(1)
        print()
