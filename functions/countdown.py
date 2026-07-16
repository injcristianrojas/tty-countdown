from datetime import datetime


def get_times(end_time: str):
    now = datetime.now().replace(microsecond=0)

    end_hour, end_minute = map(int, end_time.split(":"))
    end_dt = now.replace(hour=end_hour, minute=end_minute, second=0)

    # if end_dt <= now:
    #    end_dt += timedelta(days=1)

    time_left = end_dt - now
    total_seconds = int(time_left.total_seconds())

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    remainder_string = (
        f"{hours:02}:{minutes:02}:{seconds:02}" if total_seconds > 0 else "00:00:00"
    )

    return now.strftime("%H:%M:%S"), remainder_string
