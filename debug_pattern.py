import pandas as pd
import requests
import io
import csv

PATTERN_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdgO4JxFa_Unc-Yu4jD-FkbT0Rb5ER1xXXdV16U4tICn6YswWsP4OwqucabYtKJa7NEmq4-Jo82ojz/pub?gid=2017205813&single=true&output=csv"

def debug_pattern():
    resp = requests.get(PATTERN_URL)
    content = resp.text
    lines = content.splitlines()
    print("Pattern Sheet Headers:", lines[0])
    print("Latest 5 lines:")
    for line in lines[-5:]:
        print(line)

if __name__ == "__main__":
    debug_pattern()
