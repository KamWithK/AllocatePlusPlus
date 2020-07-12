#!/usr/bin/env python
# coding: utf-8
import os

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from hashlib import md5
from time import sleep

from selenium.webdriver.support import expected_conditions as EC

class DataManager():
    def __init__(self):
        if os.path.exists("Data.pickle"):
            self.data = pd.read_pickle("Data.pickle")
        else:
            self.driver = webdriver.Firefox()
            self.data = pd.DataFrame(columns=["Unit", "Group", "Day", "Time", "Duration"])

            self.setup_scraper()
            sleep(1)
            self.scrape()
            sleep(1)
            self.driver.quit()

    def setup_scraper(self):
        self.driver.get("https://my-timetable.monash.edu/even/student")

        try:
            WebDriverWait(self.driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, "module")))
        finally:
            # Completely load the needed DOM elements
            for code, unit in self.driver.execute_script("return data.student.student_enrolment_sem[\"Semester 2\"]").items():
                for group in unit["groups"]:
                    self.driver.execute_script("showGroup('" + md5((code + group).encode()).hexdigest() + "')")

    # Extract data
    def scrape(self):
        for unit, info in self.driver.execute_script("return data.student.student_enrolment").items():
            if unit in self.driver.execute_script("return data.student.student_enrolment_sem[\"Semester 2\"]").keys():
                for group in info["groups"].values():
                    for occasion in group["activities"].values():
                        self.data = self.data.append({
                            "Unit": unit,
                            "Group": group["activity_group_code"],
                            "Day": occasion["day_of_week"],
                            "Time": occasion["start_time"],
                            "Duration": occasion["duration"]
                        }, ignore_index=True)

    def get_data(self):
        self.data.drop_duplicates(inplace=True)
        self.data.to_pickle("Data.pickle")
        
        return self.data