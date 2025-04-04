import json

from flask import Flask, request
from flask_cors import CORS
from acquire_spectra import (acquire_spectra, find_peaks)

app = Flask(__name__)
CORS(app)
try:
	with open("version.txt","r") as f:
		version = f.read()
		app.config["VERSION"] = version
except:
     print("no version file found")

@app.route("/", methods=["GET"])
def ftmw() -> str:
    if "VERSION" not in app.config:
      app.config["VERSION"] = "0.0.0"
    return "<h1 style='color:blue'>Raston Lab FTMW API%s</h1>" % (" - Version "+app.config["VERSION"])

@app.route("/acquire_spectrum", methods=["POST"])
def acquire_spectrum() -> dict[bool, list[float], list[float]]:
    # put incoming JSON into a dictionary
    params = json.loads(request.data)
    
    # convert dictionary values to strings and return as JSON
    return acquire_spectra(params)

@app.route("/find_peaks", methods=["POST"])
def handle_peaks() -> dict[bool, dict[float, float], str]:
    params = json.loads(request.data)

    return find_peaks(
        params["x"],
        params["y"],
        float(params["threshold"]),
    )

# set debug to false in production environment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
