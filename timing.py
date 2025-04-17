import datetime
import asyncio


async def sleep_until(schedule):
    # Get the current date and time
    now = datetime.datetime.now()
    gamedays = [(gameday["Day"], gameday["AnnouncementTime"]) for gameday in schedule]
    gamedays.sort()
    # Find the soonest gameday
    soonest_gameday = None
    for gameday in gamedays:
        # Get the weekday and time components of the gameday
        weekday, time_str = gameday

        # Parse the time string into a datetime.time object
        time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()

        # Combine the weekday and time components into a datetime.datetime object
        gameday_datetime = datetime.datetime.combine(now.date(), time_obj)

        # Calculate the number of days until the next gameday
        days_until_gameday = (weekday - now.weekday() + 7) % 7
        if days_until_gameday == 0 and gameday_datetime < now:
            days_until_gameday = 7

        # Calculate the datetime for the next gameday
        next_gameday_datetime = gameday_datetime + datetime.timedelta(
            days=days_until_gameday
        )

        # If the next gameday is earlier than the soonest gameday found so far, update the soonest gameday
        if not soonest_gameday or next_gameday_datetime < soonest_gameday:
            soonest_gameday = next_gameday_datetime

    # If a soonest gameday was found, calculate the number of seconds until it and sleep for that amount of time
    if soonest_gameday:
        seconds_until_gameday = (soonest_gameday - now).total_seconds()
        await asyncio.sleep(seconds_until_gameday)
    else:
        # No soonest gameday was found, so find the soonest gameday for next week
        # Assume the first game day is the next game day
        weekday, time_str = gamedays[0]
        time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
        next_gameday_datetime = datetime.datetime.combine(
            now.date(), time_obj
        ) + datetime.timedelta(days=(7 - now.weekday() + weekday) % 7)

        # Calculate the number of seconds until the next gameday and sleep for that amount of time
        seconds_until_next_gameday = (next_gameday_datetime - now).total_seconds()
        if seconds_until_next_gameday < 0:
            seconds_until_next_gameday = (
                next_gameday_datetime + datetime.timedelta(days=7) - now
            ).total_seconds()
        await asyncio.sleep(seconds_until_next_gameday)


# Example usage:
if __name__ == "__main__":
    gamedays = [
        {"Day": 1, "AnnouncementTime": "18:30", "Times": ["19:00", "20:00"]},
        {"Day": 3, "AnnouncementTime": "18:30", "Times": ["19:00", "20:00"]},
    ]
    sleep_until(gamedays)
    print("Time to play the game!")
