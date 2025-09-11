from datetime import datetime, timedelta, time
from django.utils.timezone import now
from math import log
from numpy import ceil

def get_minutes_in_arena(arena_team):
    '''
    Compute total time spent in arena of a DWArena team

    arena_team : DWArena, the team you want to compute the time it spent in the arena

    returns : int, number of minutes the team spent in the arena
    '''
    start_dt = arena_team.date
    end_dt = now()

    total_minutes = 0
    current = start_dt

    while current.date() <= end_dt.date():
        work_start = datetime.combine(current.date(), time(9, 0), tzinfo=current.tzinfo)
        work_end = datetime.combine(current.date(), time(18, 0), tzinfo=current.tzinfo)

        # Période utile du jour
        day_start = max(current, work_start)
        day_end = min(end_dt, work_end)

        if day_start < day_end:
            total_minutes += (day_end - day_start).total_seconds() / 60

        current = datetime.combine(current.date() + timedelta(days=1), time(0, 0), tzinfo=current.tzinfo)

    return int(total_minutes)


def get_arena_coins(minutes, victories):
    '''
    Get number of diplodocoin a team earnt in arena

    minutes: int, number of minutes spent in the arena
    victories: int, number of battle the team won in the arena

    returns: int, number of diplodocins yout earned
    '''

    def logarithme(x, base):
        return log(x) / log(base)

    return max(10, ceil((minutes/5) * ((logarithme(victories, base=9)**(1/1.4)) + 1)))