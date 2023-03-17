#!/usr/bin/env python3

import argparse
from skyfield.api import load, wgs84
import numpy as np
from pytz import timezone
from colorama import just_fix_windows_console, Fore, Back, Style

def print_coverage(times, satellite_alt, timezone_str, yellow_altitude, green_altitude):
    date_fmt = '%Y-%m-%d %H:%M'
    if timezone_str is None:
        time_strings = [t.utc_datetime().strftime(date_fmt) for t in times]
    else:
        my_timezone = timezone(timezone_str)
        time_strings = [t.astimezone(my_timezone).strftime(date_fmt) for t in times]

    time_str_lin = len(time_strings[0])
    print_fmt = '%-' + str(time_str_lin) + 's %15s'
    print(Back.BLUE + print_fmt % ('Time', 'Altitude [deg]'), end='')
    print(Back.BLACK)
    for time_string, alt in zip(time_strings, satellite_alt):
        if alt < yellow_altitude:
            color = Back.RED
        elif alt < green_altitude:
            color = Back.YELLOW
        else:
            color = Back.GREEN
        print(color + '%s %15.2f' % (time_string, alt), end='')
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

    for i in range(len(times)):
        time = times[i]
        for satellite in satellites:
            difference = satellite - here
            alt, az, distance = difference.at(time).altaz()
            satellite_alt[i] = max(satellite_alt[i], alt.degrees)

    return times, satellite_alt

parser = argparse.ArgumentParser()
parser.add_argument('time_hours', help='time in hours (default 12)', default=12, nargs='?', type=float)
parser.add_argument('dt_mins', help='time period in minutes (default 15)', default=15, nargs='?', type=float)
parser.add_argument('lat', help='latitude in degrees (default Seattle, WA)', default=47.608013, nargs='?', type=float)
parser.add_argument('lon', help='longitude in degrees (default Seattle, WA)', default=-122.335167, nargs='?', type=float)
parser.add_argument('--oneweb', help='oneweb satellites', action='store_true')
parser.add_argument('--starlink', help='starlink satellites', action='store_true')
parser.add_argument('--iss', help='iss', action='store_true')
parser.add_argument('--timezone', help='timezone for plotting (default is UTC)', default=None, type=str)
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

times, satellite_alt = propagate(satellites, args.lat, args.lon, args.time_hours*3600, args.dt_mins*60)
print_coverage(times, satellite_alt, args.timezone, args.yellow_altitude, args.green_altitude)