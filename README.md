# `whatsup.py`

Simple tool to show what your satellite coverage in the near future. It looks at all satellites visible from your current location, and chooses the one highest in the sky. When you run the tool it pulls the latest TLEs from [Celestrak](https://celestrak.org/), and propagates the satellite orbits using [Skyfield](https://rhodesmill.org/skyfield/).

## Usage

To see what the Starlink coverage over Seattle for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 47.608013 -122.335167 --starlink --timezone US/Pacific
```

To see what the OneWeb coverage over Seattle for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 47.608013 -122.335167 --oneweb --timezone US/Pacific
```

To see when the ISS is over Seattle for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 47.608013 -122.335167 --iss --timezone US/Pacific
```

To see when the ISS is over [Null Island](https://en.wikipedia.org/wiki/Null_Island) (lat/lon = 0) for the next 5 hours looks like (in 15 minute increments):

```
./whatsup.py 5 15 0 0 --iss
```