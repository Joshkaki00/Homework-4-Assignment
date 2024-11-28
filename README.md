# Weather Application

This is a Flask-based web application that allows users to get current weather conditions and compare weather data between two cities using the OpenWeatherMap API.

## Setup

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your OpenWeatherMap API key:
    ```plaintext
    API_KEY=your_api_key_here
    ```

5. Run the application:
    ```bash
    flask run
    ```

## Dependencies

- Flask
- Requests
- PrettyPrinter
- datetime
- dotenv
- geopy

## License

This project is licensed under the MIT License.