# `whatsup.py`

Simple tool to show your satellite coverage in the near future. It looks at satellite(s) visible from your current location, and chooses the one highest in the sky. When you run the tool it pulls the latest TLEs from [Celestrak](https://celestrak.org/), and propagates the satellite orbits using [Skyfield](https://rhodesmill.org/skyfield/).

## Install Requirements

```
pip install -r requirements.txt
```

## Usage

```
usage: whatsup.py [-h] [--oneweb] [--starlink] [--iss] [--timezone TIMEZONE] [--yellow_altitude YELLOW_ALTITUDE] [--green_altitude GREEN_ALTITUDE]
                  [time_hours] [dt_mins] [lat] [lon]

positional arguments:
  time_hours            time in hours (default 12)
  dt_mins               time period in minutes (default 15)
  lat                   latitude in degrees (default Seattle, WA)
  lon                   longitude in degrees (default Seattle, WA)

optional arguments:
  -h, --help            show this help message and exit
  --oneweb              oneweb satellites
  --starlink            starlink satellites
  --iss                 iss
  --timezone TIMEZONE   timezone for plotting (default is UTC)
  --yellow_altitude YELLOW_ALTITUDE
                        satellite altitude to color yellow (default 55)
  --green_altitude GREEN_ALTITUDE
                        satellite altitude to color green (default 70)
```

To see what the OneWeb coverage over Seattle for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 47.608013 -122.335167 --oneweb --timezone US/Pacific
```

You'll see something like this:
![oneweb coverage](https://github.com/friedman101/whatsup/blob/main/pics/oneweb.png?raw=true)


To see what the Starlink coverage over Seattle for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 47.608013 -122.335167 --starlink --timezone US/Pacific
```

To see when the ISS is over Seattle for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 47.608013 -122.335167 --iss --timezone US/Pacific
```

To see when the ISS is over [Null Island](https://en.wikipedia.org/wiki/Null_Island) (lat/lon = 0) for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 0 0 --iss
```