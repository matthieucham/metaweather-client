# metaweather-client
A simple Metaweather API client, to know if it's raining today in a given city

Using https://www.metaweather.com/api/

## Dependencies
- Python >= 3.4
- Requests 2.21.0
- python-dateutil 2.8.0

You can install all deps in a virtual env with:

`> pip install -r requirements.txt`

## Usage

`> will_it_rain_in.py -h`

>usage: will_it_rain_in.py [-h] city [city ...]
>
>Display today's weather forecast in a given city using MetaWeather API
>
>positional arguments:
>  city        City name, e.g. 'New York' or 'Toulouse'
>
>optional arguments:
>  -h, --help  show this help message and exit


## Example

`> will_it_rain_in.py new york`
> Today in New York, New York : Light Cloud so NO RAIN (predictability 70%)

`> will_it_rain_in.py delhi`
> Today in New Delhi, India : Heavy Rain so YES SOME RAIN OR WORSE (predictability 77%)

