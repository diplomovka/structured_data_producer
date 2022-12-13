from flask import Flask
from blueprints.structured_data_producer_routes import structured_data_producer_routes

app = Flask(__name__)
app.register_blueprint(structured_data_producer_routes, url_prefix='/structured-data')

@app.route('/')
def main_route():
    return '<p>routes /structured-data </p>' 

if __name__ == '__main__':
    app.run()