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
API_URL = 'https://api.openweathermap.org/data/3.0/onecall'

def get_weather_data(lat, lon, units):
    params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,hourly',
        'units': units,
        'appid': API_KEY
    }
    response = requests.get(API_URL, params=params)
    return response.json()

def get_coordinates(city):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city)
    return location.latitude, location.longitude

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
    city = request.args.get('city')
    units = request.args.get('units', 'metric')

    lat, lon = get_coordinates(city)
    result_json = get_weather_data(lat, lon, units)

    context = {
        'date': datetime.now(),
        'city': city,
        'description': result_json['current']['weather'][0]['description'],
        'temp': result_json['current']['temp'],
        'humidity': result_json['current']['humidity'],
        'wind_speed': result_json['current']['wind_speed'],
        'sunrise': datetime.fromtimestamp(result_json['current']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['current']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units', 'metric')

    lat1, lon1 = get_coordinates(city1)
    lat2, lon2 = get_coordinates(city2)

    result_json1 = get_weather_data(lat1, lon1, units)
    result_json2 = get_weather_data(lat2, lon2, units)

    city1_info = {
        'city': city1,
        'temp': result_json1['current']['temp'],
        'humidity': result_json1['current']['humidity'],
        'wind_speed': result_json1['current']['wind_speed'],
        'sunset': datetime.fromtimestamp(result_json1['current']['sunset'])
    }

    city2_info = {
        'city': city2,
        'temp': result_json2['current']['temp'],
        'humidity': result_json2['current']['humidity'],
        'wind_speed': result_json2['current']['wind_speed'],
        'sunset': datetime.fromtimestamp(result_json2['current']['sunset'])
    }

    context = {
        'city1_info': city1_info,
        'city2_info': city2_info,
        'units_letter': get_letter_for_units(units)
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
