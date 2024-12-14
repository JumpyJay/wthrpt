import os
import requests
import datetime



from flask import redirect, render_template, request, session
from functools import wraps



def sorry(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("sorry.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(city_name):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = '6938f97794cd7674b8a6ad7af45072b5'
        url = f"https://api.openweathermap.org/data/2.5/weather?units=metric&q={city_name}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        quoted = quote['main']
        quotez = quote['weather']
        quotee = quotez[0]
        quotef = quote['wind']
        quoteh = quote['clouds']
        quotei = quote['sys']

        return {
            "visi": int(quote["visibility"]),
            "temp": float(quoted["temp"]),
            "flike": float(quoted["feels_like"]),
            "maxt": float(quoted["temp_max"]),
            "mint": float(quoted["temp_min"]),
            "pres": int(quoted["pressure"]),
            "humi": int(quoted["humidity"]),
            "mainw": quotee["main"],
            "desw": quotee["description"],
            "wspd": float(quotef["speed"]),
            "wdg": int(quotef["deg"]),
            "cld": int(quoteh["all"]),
            "sunr": datetime.datetime.fromtimestamp(int(quotei["sunrise"])),
            "suns": datetime.datetime.fromtimestamp(int(quotei["sunset"])),
            "cntr": quotei["country"]
        }

    except (KeyError, TypeError, ValueError):
        return None


def lookin(city_name):
    try:
        api_key = '6938f97794cd7674b8a6ad7af45072b5'
        url = f"https://api.openweathermap.org/data/2.5/weather?units=metric&q={city_name}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        quote = response.json()
        quoted = quote['main']
        quotei = quote['sys']
        quotez = quote['weather']
        quotee = quotez[0]

        return {
            "temp": float(quoted["temp"]),
            "cntr": quotei["country"],
            "mainw": quotee["main"],
        }

    except (KeyError, TypeError, ValueError):
        return None




