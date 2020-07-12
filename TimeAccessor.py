#!/usr/bin/env python
# coding: utf-8

import pandas as pd

from math import trunc

def collision(entry_1, entry_2):
    # Assume duration is always relatively short
    if entry_1["Day"] != entry_2["Day"]:
        return False
    
    # Starting at the same time implies a collision
    if entry_1["Day"] == entry_2["Day"] and entry_1["Time"] == entry_2["Time"]:
        return True

    start_time = [entry_1["Time"], entry_2["Time"]]
    end_time = [get_end_date(entry_1), get_end_date(entry_2)]

    if (before(start_time[0], start_time[1]) and before(end_time[0], start_time[1])) or (before(start_time[1], start_time[0]) and before(end_time[1], start_time[0])):
        return False
    return True

def before(time_1, time_2):
    if time_1[0] < time_2[0] or (time_1[0] == time_2[0] and time_1[1] <= time_2[1]):
        return True
    return False

def get_end_date(entry):
    duration = (trunc(entry["Duration"]/60), entry["Duration"] % 60)
    
    hours = entry["Time"][0] + duration[0] + trunc((entry["Time"][1] + duration[1])/60)
    minutes = (entry["Time"][1] + duration[1]) % 60

    return (hours, minutes)

@pd.api.extensions.register_dataframe_accessor("week_time")
class WeekTimeAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj
    
    @staticmethod
    def _validate(obj):
        if "Time" not in obj.columns or "Day" not in obj.columns:
            raise AttributeError("Must have 'Time' and 'Day'")

    def set_compute_values(self):
        self._obj["Time"] = self._obj["Time"].apply(lambda time : (int(time.split(":")[0]), int(time.split(":")[1])))
        self._obj["Duration"] = pd.to_numeric(self._obj["Duration"])

    def set_visual_values(self):
        self._obj["Time"] = self._obj["Time"].apply(lambda time : str(time[0]) + ":" + str(time[1]).zfill(2))

    @property
    def time_collides(self):
        self.set_compute_values()

        data = pd.DataFrame(columns=["Mon", "Tue", "Wed", "Thu", "Fri"], index=range(1, 25))

        for day in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
            for time in range(1, 25):
                time_slot = {"Day": day, "Time": (time, 00), "Duration": 60}

                data[day][time] = self._obj.apply(collision, axis=1, args=[time_slot]).sum()

        self.set_visual_values()
        return data
