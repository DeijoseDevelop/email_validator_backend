from src.config import app
from src.api.views import api_blueprint


app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)