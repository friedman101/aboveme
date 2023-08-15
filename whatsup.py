#!/usr/bin/env python3

import argparse
from skyfield.api import load, wgs84
import numpy as np
from pytz import timezone
from colorama import init, deinit, Fore, Back, Style
import requests
import urllib.parse
from timezonefinder import TimezoneFinder
import termplotlib as tpl

def latlontz_from_city(city):
    url = 'https://nominatim.openstreetmap.org/search?q=' + city +'&format=json'
    response = requests.get(url).json()
    lat = float(response[0]['lat'])
    lon = float(response[0]['lon'])
    tz = TimezoneFinder().timezone_at(lat=lat,lng=lon)
    return lat, lon, tz

def plot_coverage(times, satellite_alt, timezone_str):
    date_fmt = '%H.%M'
    if timezone_str == 'UTC':
        time_strings = [t.utc_datetime().strftime(date_fmt) for t in times]
    else:
        my_timezone = timezone(timezone_str)
        time_strings = [t.astimezone(my_timezone).strftime(date_fmt) for t in times]

    # convert to fractional hours instead of hours.minutes
    time_hours_mins = np.array([float(t) for t in time_strings])
    time_hours = np.floor(time_hours_mins)
    time_mins = (time_hours_mins - time_hours)
    time_hours_frac = time_hours + time_mins*100/60
    # unwrap the hours, so [23 0 1] becomes [23 24 25]
    time_hours_frac = np.unwrap(time_hours_frac, period=24)

    fig = tpl.figure()
    fig.plot(time_hours_frac,satellite_alt,xlabel='time [hr]',title='altitude [deg]')
    fig.show()

def print_coverage_table(times, satellite_alt, satellite_name, timezone_str, yellow_altitude, green_altitude):
    date_fmt = '%Y-%m-%d %H:%M'
    if timezone_str == 'UTC':
        time_strings = [t.utc_datetime().strftime(date_fmt) for t in times]
    else:
        my_timezone = timezone(timezone_str)
        time_strings = [t.astimezone(my_timezone).strftime(date_fmt) for t in times]

    time_str_lin = len(time_strings[0])
    print_fmt = '%-' + str(time_str_lin) + 's %15s %15s'
    init(autoreset=True)
    print(Back.BLUE + print_fmt % ('Time', 'Satellite Name', 'Altitude [deg]'), end='')
    print(Back.BLACK)
    for time_string, name, alt in zip(time_strings, satellite_name, satellite_alt):
        if alt < yellow_altitude:
            color = Back.RED
        elif alt < green_altitude:
            color = Back.YELLOW
        else:
            color = Back.GREEN
        print(color + '%s %15s %15.1f' % (time_string, name, alt), end='')
        print(Back.BLACK)

def propagate(satellites, lat, lon, propagation_time, dt):
    here = wgs84.latlon(lat, lon)
    ts = load.timescale()
    t0 = ts.now()
    start_time = t0
    end_time = t0 + propagation_time/3600/24
    times = np.arange(start_time, end_time, dt/3600/24)
    times_tt = np.array([t.tt for t in times])
    satellite_alt = np.zeros(len(times))
    satellite_name = ['']*len(times)

    for i in range(len(times)):
        time = times[i]
        for satellite in satellites:
            difference = satellite - here
            alt, az, distance = difference.at(time).altaz()
            if alt.degrees > satellite_alt[i]:
                satellite_alt[i] = alt.degrees
                satellite_name[i] = satellite.name

    return times, satellite_alt, satellite_name

parser = argparse.ArgumentParser()
parser.add_argument('time_hours', help='time in hours (default 12)', default=12, nargs='?', type=float)
parser.add_argument('dt_mins', help='time period in minutes (default 15)', default=15, nargs='?', type=float)
parser.add_argument('city', help='city name (default Seattle, WA)', default='Seattle, WA', nargs='?', type=str)
parser.add_argument('--oneweb', help='oneweb satellites', action='store_true')
parser.add_argument('--starlink', help='starlink satellites', action='store_true')
parser.add_argument('--iss', help='iss', action='store_true')
parser.add_argument('--utc', help='use UTC time instead of local time', action='store_true')
parser.add_argument('--yellow_altitude', help='satellite altitude to color yellow (default 55)', default=55.0, type=float)
parser.add_argument('--green_altitude', help='satellite altitude to color green (default 70)', default=70.0, type=float)
args = parser.parse_args()

tle_url = {}
tle_url['oneweb'] = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=tle'
tle_url['starlink'] = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle'
tle_url['iss'] = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle'
satellites = []
if args.oneweb:
    satellites += load.tle_file(tle_url['oneweb'], reload=True)
if args.starlink:
    satellites += load.tle_file(tle_url['starlink'], reload=True)
if args.iss:
    satellites += load.tle_file(tle_url['iss'], reload=True)
    by_name = {sat.name: sat for sat in satellites}
    satellites = [by_name['ISS (ZARYA)']]

lat, lon, tz = latlontz_from_city(args.city)
if args.utc:
    tz = 'UTC'
times, satellite_alt, satellite_name = propagate(satellites, lat, lon, args.time_hours*3600, args.dt_mins*60)
print_coverage_table(times, satellite_alt, satellite_name, tz, args.yellow_altitude, args.green_altitude)
plot_coverage(times, satellite_alt, tz)