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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Oops! The page you're looking for doesn't exist."), 404

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

    # Error handling for invalid city or API failure
    if result_json.get('cod') != 200:
        return render_template('404.html', message="City not found"), 404

    context = {
        'date': datetime.now(),
        'city': result_json.get('name', ''),
        'description': result_json['weather'][0]['description'] if 'weather' in result_json else '',
        'temp': result_json['main']['temp'] if 'main' in result_json else '',
        'humidity': result_json['main']['humidity'] if 'main' in result_json else '',
        'wind_speed': result_json['wind']['speed'] if 'wind' in result_json else '',
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']) if 'sys' in result_json and 'sunrise' in result_json['sys'] else '',
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']) if 'sys' in result_json and 'sunset' in result_json['sys'] else '',
        'units_letter': get_letter_for_units(units),
        'icon': result_json['weather'][0]['icon'] if 'weather' in result_json else ''  # Add the icon
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""

    city1 = request.args.get('city1', '')
    city2 = request.args.get('city2', '')
    units = request.args.get('units', 'imperial')

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
    'sunset': datetime.fromtimestamp(city1_data['sys']['sunset']) if 'sys' in city1_data else '',
    }

    city2_info = {
    'city': city2_data.get('name', ''),
    'temp': city2_data['main']['temp'] if 'main' in city2_data else '',
    'humidity': city2_data['main']['humidity'] if 'main' in city2_data else '',
    'wind_speed': city2_data['wind']['speed'] if 'wind' in city2_data else '',
    'sunset': datetime.fromtimestamp(city2_data['sys']['sunset']) if 'sys' in city2_data else '',
    }

    # Calculate absolute differences
    abs_humidity_difference = abs(city1_info['humidity'] - city2_info['humidity'])
    abs_wind_speed_difference = abs(city1_info['wind_speed'] - city2_info['wind_speed'])
    abs_sunset_difference = abs((city1_info['sunset'] - city2_info['sunset']).total_seconds() / 3600) if city1_info['sunset'] and city2_info['sunset'] else None

    context = {
        'city1_info': city1_info,
        'city2_info': city2_info,
        'units_letter': get_letter_for_units(units),
        'date': datetime.now(),
        'abs_humidity_difference': abs_humidity_difference,
        'abs_wind_speed_difference': abs_wind_speed_difference,
        'abs_sunset_difference': abs_sunset_difference
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True, port=3000)
