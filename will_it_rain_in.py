import argparse
import urllib.parse


class FormatCityName(argparse.Action):
    """
    Concatenate args input into one escaped, ready-to-be-requested string
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, urllib.parse.quote_plus(' '.join(values), encoding='utf8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Display today's weather forecast in a given city using MetaWeather API")
    parser.add_argument('city', nargs='+', help="City name, e.g. 'New York' or 'Toulouse'", action=FormatCityName)
    args = parser.parse_args()
    print(args.city)
