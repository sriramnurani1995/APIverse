from flask import render_template
from flask.views import MethodView

class Index(MethodView):
    def get(self):
        """Render the home page."""
        return render_template('index.html')