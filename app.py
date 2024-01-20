"""Module to contain and run the endpoints for the Deloton staff API"""

from datetime import datetime
from flask import Flask, current_app, render_template
from jinja2 import Template, Environment, FileSystemLoader


app = Flask(__name__, template_folder='templates')
app.json.sort_keys = False



@app.route("/", methods=["GET"])
def index():
    """ Creates an index route with an index page for the API """
    counters = [[] for i in range(29)]
    counters[28].append('fuchsia')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[28].append('khaki')
    counters[13].append('ochre')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    counters[8].append('khaki')
    return render_template('game.html', counters = counters)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
