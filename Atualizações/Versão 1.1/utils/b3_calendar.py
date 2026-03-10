import datetime

def get_easter(year):
    """
    Calculates Easter Sunday using the Anonymous Gregorian algorithm.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def get_b3_holidays(year):
    """
    Returns a set of B3 non-trading dates for a given year.
    Includes National Holidays and B3-specific closures.
    """
    holidays = set()
    
    # Fixed Holidays
    holidays.add(datetime.date(year, 1, 1))   # New Year
    holidays.add(datetime.date(year, 4, 21))  # Tiradentes
    holidays.add(datetime.date(year, 5, 1))   # Labor Day
    holidays.add(datetime.date(year, 9, 7))   # Independence
    holidays.add(datetime.date(year, 10, 12)) # Our Lady of Aparecida
    holidays.add(datetime.date(year, 11, 2))  # All Souls
    holidays.add(datetime.date(year, 11, 15)) # Republic Proclamation
    holidays.add(datetime.date(year, 11, 20)) # Black Awareness Day (National since 2024)
    holidays.add(datetime.date(year, 12, 25)) # Christmas
    
    # Dec 31 is usually non-trading for B3
    holidays.add(datetime.date(year, 12, 31))
    
    # Variable Holidays (Relative to Easter)
    easter = get_easter(year)
    holidays.add(easter - datetime.timedelta(days=2)) # Good Friday (Sexta-feira Santa)
    holidays.add(easter - datetime.timedelta(days=47)) # Carnival Monday
    holidays.add(easter - datetime.timedelta(days=48)) # Carnival Tuesday
    holidays.add(easter + datetime.timedelta(days=60)) # Corpus Christi
    
    return holidays

def is_trading_day(date):
    """
    Checks if a date is a valid B3 trading day (not a weekend or holiday).
    """
    if date.weekday() >= 5: # Saturday = 5, Sunday = 6
        return False
    
    holidays = get_b3_holidays(date.year)
    if date in holidays:
        return False
        
    return True
