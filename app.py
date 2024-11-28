import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'https://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city', '')
    units = request.args.get('units', 'imperial')

    params = {
        'q': city,
        'appid': API_KEY,
        'units': units
    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now(),
        'city': result_json.get('name', ''),
        'description': result_json['weather'][0]['description'] if 'weather' in result_json else '',
        'temp': result_json['main']['temp'] if 'main' in result_json else '',
        'humidity': result_json['main']['humidity'] if 'main' in result_json else '',
        'wind_speed': result_json['wind']['speed'] if 'wind' in result_json else '',
        'sunrise': result_json['sys']['sunrise'] if 'sys' in result_json else '',
        'sunset': result_json['sys']['sunset'] if 'sys' in result_json else '',
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1', '')
    city2 = request.args.get('city2', '')
    units = request.args.get('units', 'imperial')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!

    def fetch_weather(city, units):
        params = {
            'q': city,
            'appid': API_KEY,
            'units': units}
        response = requests.get(API_URL, params=params)
        return response.json()

    city1_data = fetch_weather(city1, units)
    city2_data = fetch_weather(city2, units)

    city1_info = {
        'city': city1_data.get('name', ''),
        'temp': city1_data['main']['temp'] if 'main' in city1_data else '',
        'humidity': city1_data['main']['humidity'] if 'main' in city1_data else '',
        'wind_speed': city1_data['wind']['speed'] if 'wind' in city1_data else '',
        'sunset': datetime.fromtimestamp(city1_data['sys']['sunset']) if 'sys' in city1_data else ''
    }

    city2_info = {
        'city': city2_data.get('name', ''),
        'temp': city2_data['main']['temp'] if 'main' in city2_data else '',
        'humidity': city2_data['main']['humidity'] if 'main' in city2_data else '',
        'wind_speed': city2_data['wind']['speed'] if 'wind' in city2_data else '',
        'sunset': datetime.fromtimestamp(city2_data['sys']['sunset']) if 'sys' in city2_data else ''
    }

    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    context = {
        'city1_info': city1_info,
        'city2_info': city2_info,
        'units_letter': get_letter_for_units(units)
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
