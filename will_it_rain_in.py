import sys
import argparse
import requests
import urllib.parse
import json
from datetime import datetime
import dateutil.parser


class BaseWillItRainInException(Exception):
    pass


class RemoteServiceError(BaseWillItRainInException):
    pass


class LocationNotFound(BaseWillItRainInException):
    pass


class TooManyLocations(BaseWillItRainInException):
    pass


class NoForecastForToday(BaseWillItRainInException):
    pass


class MetaweatherService(object):

    def _json_parse_mw_response(self, resp):
        """
        Parse API response as a JSON content, raise exceptions if don't go well
        :param resp: requests' Response instance
        :return: resp.text parsed as JSON if resp.status_code is ok
        """
        if not resp.ok:
            raise RemoteServiceError('Bad response status %s' % resp.status_code)
        try:
            json_resp = json.loads(resp.text)
        except json.JSONDecodeError:
            raise RemoteServiceError('Bad response content')
        return json_resp

    def _mw_location_search(self, city):
        """
        Performs Metaweather location search query
        :param city: query value
        :return: Response from requests
        """
        return requests.get('https://www.metaweather.com/api/location/search/', {'query': city})

    def _mw_location_get(self, woeid):
        """
        Performs Metaweather forecast get query
        :param woeid: location Id, provided by mw_location_search
        :return: Forecast in this location
        """
        return requests.get('https://www.metaweather.com/api/location/%s/' % woeid)

    def get_matching_locations(self, city, max_locations=5):
        """
        Find locations provided by Metaweather, matching the requested city
        :param city: Requested city name, or part of it
        :param max_locations: maximum number of matching location. If above limit, raises TooManyLocations exception
        :return: List of found locations
        """
        mw_location_search_resp = self._mw_location_search(city)
        json_locations = self._json_parse_mw_response(mw_location_search_resp)
        if len(json_locations) > max_locations:
            raise TooManyLocations()
        if len(json_locations) == 0:
            raise LocationNotFound()
        return json_locations

    def get_todays_forecast_in_location(self, woeid):
        """
        Get today's forecast in the requested location
        :param woeid: Location's WOEID
        :return: forecast of the day
        """
        mw_location_get_resp = self._mw_location_get(woeid)
        json_forecast = self._json_parse_mw_response(mw_location_get_resp)
        # To avoid timezone issues, let's assume that "today" means "the day it is currently at the location"
        today = dateutil.parser.parse(json_forecast['time']).strftime('%Y-%m-%d')  # since MW API uses this format
        today_weather = None
        for cw in json_forecast.pop('consolidated_weather'):
            if cw['applicable_date'] == today:
                today_weather = cw
                break
        if today_weather is None:
            raise NoForecastForToday(today)
        location_details = json_forecast  # Renaming because there's only location info left in json_forecast
        return location_details, today_weather


class FormatCityNameArg(argparse.Action):
    """
    Concatenate args input into one escaped, ready-to-be-requested string
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))


def format_location(location_info):
    city = location_info['title']
    if 'title' in location_info.get('parent'):
        city = "%s, %s" % (location_info['title'], location_info['parent']['title'])
    return city


def format_weather(consolidated_weather):
    no_rain_abbr = ['c', 'lc', 'hc']
    data = {'weather_state': consolidated_weather['weather_state_name'],
            'predictability': consolidated_weather['predictability'],
            'rain': 'NO RAIN' if consolidated_weather['weather_state_abbr'] in no_rain_abbr
            else 'YES SOME RAIN OR WORSE'}
    return '{weather_state} so {rain} (predictability {predictability}%)'.format(**data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Display today's weather forecast in a given city using MetaWeather API")
    parser.add_argument('city', nargs='+', help="City name, e.g. 'New York' or 'Toulouse'", action=FormatCityNameArg)
    args = parser.parse_args()
    mw_service = MetaweatherService()
    try:
        locations = mw_service.get_matching_locations(args.city)
    except RemoteServiceError as rse:
        sys.exit("Remote forecasting service call has failed with the following message: %s " % str(rse))
    except LocationNotFound:
        sys.exit("Unknown city '%s'" % args.city)
    except TooManyLocations:
        sys.exit("Too many locations found matching the requested argument, please refine and try again")
    for loc in locations:
        loc_info, weather = mw_service.get_todays_forecast_in_location(loc['woeid'])
        print("Today in {} : {}".format(format_location(loc_info), format_weather(weather)))
