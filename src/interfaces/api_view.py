from flask.views import MethodView
from flasgger import SwaggerView


class APIView(SwaggerView, MethodView):
    pass