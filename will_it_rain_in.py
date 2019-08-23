import argparse
import requests
import urllib.parse

MW_API_URL = 'https://www.metaweather.com/api/%s/'


class BaseWillItRainInException(Exception):
    pass


class MetaweatherError(BaseWillItRainInException):
    pass


class TooManyLocations(BaseWillItRainInException):
    pass


def mw_location_search(city):
    """
    Performs metaweather location search query
    :param city: query value
    :return: Response from requests
    """
    return requests.get('https://www.metaweather.com/api/location/search/', {'query': city})


def get_matching_locations(city, max_locations=5):
    """
    Find locations provided by Metaweather, matching the requested city
    :param city: Requested city name, or part of it
    :param max_locations: maximum number of matching location. If above limit, raises TooManyLocations exception
    :return: List of found locations
    """
    mw_location_search_resp = mw_location_search(city)
    if not mw_location_search_resp.status_code == 200:
        raise MetaweatherError()


class FormatCityName(argparse.Action):
    """
    Concatenate args input into one escaped, ready-to-be-requested string
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Display today's weather forecast in a given city using MetaWeather API")
    parser.add_argument('city', nargs='+', help="City name, e.g. 'New York' or 'Toulouse'", action=FormatCityName)
    args = parser.parse_args()
    print(args.city)

    mw_location_search_resp = mw_location_search(args.city)
