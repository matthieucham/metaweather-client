import unittest
from unittest.mock import Mock, patch, MagicMock, create_autospec

import will_it_rain_in
from requests import Response


class TestWillItRainIn(unittest.TestCase):

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_search')
    def test_mw_location_search_error404(self, mock_mw_location_search):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.status_code = 404
        mock_service_response.ok = False
        mock_mw_location_search.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.RemoteServiceError, mw_service.get_matching_locations, 'Toulouse')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_search')
    def test_mw_location_search_error500(self, mock_mw_location_search):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.status_code = 500
        mock_service_response.ok = False
        mock_mw_location_search.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.RemoteServiceError, mw_service.get_matching_locations, 'Toulouse')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_search')
    def test_mw_location_search_badcontent(self, mock_mw_location_search):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.ok = True
        mock_service_response.text = 'blablabla'
        mock_mw_location_search.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.RemoteServiceError, mw_service.get_matching_locations, 'Toulouse')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_search')
    def test_mw_location_search_notfound(self, mock_mw_location_search):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.ok = True
        mock_service_response.text = '[]'
        mock_mw_location_search.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.LocationNotFound, mw_service.get_matching_locations, 'ezrgtury')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_search')
    def test_mw_location_search_toomany(self, mock_mw_location_search):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.ok = True
        mock_service_response.text = \
            '[{"title":"Houston","location_type":"City","woeid":2424766,"latt_long":"29.760450,-95.369781"},\
            {"title":"Tokyo","location_type":"City","woeid":1118370,"latt_long":"35.670479,139.740921"},\
            {"title":"Bristol","location_type":"City","woeid":13963,"latt_long":"51.453732,-2.591560"},\
            {"title":"San Antonio","location_type":"City","woeid":2487796,"latt_long":"29.424580,-98.494614"},\
            {"title":"Toronto","location_type":"City","woeid":4118,"latt_long":"43.648560,-79.385368"},\
            {"title":"Washington DC","location_type":"City","woeid":2514815,"latt_long":"38.899101,-77.028999"},\
            {"title":"Boston","location_type":"City","woeid":2367105,"latt_long":"42.358631,-71.056702"},\
            {"title":"Sacramento","location_type":"City","woeid":2486340,"latt_long":"38.579060,-121.491013"},\
            {"title":"Wilmington","location_type":"City","woeid":2521358,"latt_long":"39.740231,-75.550842"}]'
        mock_mw_location_search.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.TooManyLocations, mw_service.get_matching_locations, 'to')
        # change limit = accept more responses, so the call should succeed
        mw_service.get_matching_locations('to', max_locations=10)
        self.assertTrue(True)

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_get')
    def test_mw_location_get_error(self, mock_mw_location_get):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.status_code = 500
        mock_service_response.ok = False
        mock_mw_location_get.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.RemoteServiceError, mw_service.get_todays_forecast_in_location, '2514815')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_get')
    def test_mw_location_get_badcontent(self, mock_mw_location_get):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.status_code = 500
        mock_service_response.ok = False
        mock_service_response.text = 'blablabla'
        mock_mw_location_get.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.RemoteServiceError, mw_service.get_todays_forecast_in_location, '2514815')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_get')
    def test_mw_location_get_noforecasttoday(self, mock_mw_location_get):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.ok = True
        # Time and applicable_date not the same day :
        mock_service_response.text = '{"consolidated_weather": \
            [{"applicable_date": "2019-08-27"}], "time": "2019-08-26T13:24:26.194766+02:00", "title": "Toulouse"}'
        mock_mw_location_get.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        self.assertRaises(will_it_rain_in.NoForecastForToday, mw_service.get_todays_forecast_in_location, '2514815')

    @patch.object(will_it_rain_in.MetaweatherService, '_mw_location_get')
    def test_mw_location_get_nominal(self, mock_mw_location_get):
        # test setup
        mock_service_response = create_autospec(Response)
        mock_service_response.ok = True
        # Time and applicable_date not the same day :
        mock_service_response.text = '{"consolidated_weather":[{"id":6169383070072832,"weather_state_name":"Light Cloud","weather_state_abbr":"lc","wind_direction_compass":"NE","created":"2019-08-26T12:05:44.752613Z","applicable_date":"2019-08-26","min_temp":15.975,"max_temp":20.73,"the_temp":19.439999999999998,"wind_speed":6.04626446734537,"wind_direction":53.77575057860458,"air_pressure":1023.1800000000001,"humidity":65,"visibility":15.060484271852381,"predictability":70},{"id":6098275524411392,"weather_state_name":"Light Cloud","weather_state_abbr":"lc","wind_direction_compass":"E","created":"2019-08-26T12:05:47.126637Z","applicable_date":"2019-08-27","min_temp":16.945,"max_temp":25.46,"the_temp":21.89,"wind_speed":4.68247138761632,"wind_direction":99.25930652903241,"air_pressure":1021.1800000000001,"humidity":56,"visibility":14.698224866778016,"predictability":70},{"id":5606433116651520,"weather_state_name":"Showers","weather_state_abbr":"s","wind_direction_compass":"SE","created":"2019-08-26T12:05:50.256701Z","applicable_date":"2019-08-28","min_temp":20.09,"max_temp":27.17,"the_temp":23.880000000000003,"wind_speed":4.773376289556987,"wind_direction":134.00101701768259,"air_pressure":1016.2950000000001,"humidity":64,"visibility":12.319926628489622,"predictability":73},{"id":5662333726621696,"weather_state_name":"Heavy Cloud","weather_state_abbr":"hc","wind_direction_compass":"W","created":"2019-08-26T12:05:53.309760Z","applicable_date":"2019-08-29","min_temp":21.77,"max_temp":29.604999999999997,"the_temp":27.305,"wind_speed":5.54332950878072,"wind_direction":271.7673334583674,"air_pressure":1013.825,"humidity":54,"visibility":15.127592360614013,"predictability":71},{"id":5586725457887232,"weather_state_name":"Heavy Cloud","weather_state_abbr":"hc","wind_direction_compass":"W","created":"2019-08-26T12:05:56.137950Z","applicable_date":"2019-08-30","min_temp":20.895,"max_temp":30.015,"the_temp":28.195,"wind_speed":5.7625084363530314,"wind_direction":274.76329142576714,"air_pressure":1015.0,"humidity":48,"visibility":15.899646066968902,"predictability":71},{"id":5996392390590464,"weather_state_name":"Light Cloud","weather_state_abbr":"lc","wind_direction_compass":"WSW","created":"2019-08-26T12:05:59.116503Z","applicable_date":"2019-08-31","min_temp":21.16,"max_temp":29.895,"the_temp":25.99,"wind_speed":5.237591068161934,"wind_direction":240.99999999999997,"air_pressure":1017.63,"humidity":47,"visibility":9.999726596675416,"predictability":70}],"time":"2019-08-26T08:35:20.417023-04:00","sun_rise":"2019-08-26T06:16:55.724895-04:00","sun_set":"2019-08-26T19:38:05.624145-04:00","timezone_name":"LMT","parent":{"title":"New York","location_type":"Region / State / Province","woeid":2347591,"latt_long":"42.855350,-76.501671"},"sources":[{"title":"BBC","slug":"bbc","url":"http://www.bbc.co.uk/weather/","crawl_rate":360},{"title":"Forecast.io","slug":"forecast-io","url":"http://forecast.io/","crawl_rate":480},{"title":"HAMweather","slug":"hamweather","url":"http://www.hamweather.com/","crawl_rate":360},{"title":"Met Office","slug":"met-office","url":"http://www.metoffice.gov.uk/","crawl_rate":180},{"title":"OpenWeatherMap","slug":"openweathermap","url":"http://openweathermap.org/","crawl_rate":360},{"title":"Weather Underground","slug":"wunderground","url":"https://www.wunderground.com/?apiref=fc30dc3cd224e19b","crawl_rate":720},{"title":"World Weather Online","slug":"world-weather-online","url":"http://www.worldweatheronline.com/","crawl_rate":360}],"title":"New York","location_type":"City","woeid":2459115,"latt_long":"40.71455,-74.007118","timezone":"US/Eastern"}'
        mock_mw_location_get.return_value = mock_service_response

        # service call
        mw_service = will_it_rain_in.MetaweatherService()
        loc, weather = mw_service.get_todays_forecast_in_location('2459115')
        self.assertEqual("New York", loc['title'])
        self.assertEqual("lc", weather['weather_state_abbr'])
        self.assertEqual(70, weather['predictability'])
