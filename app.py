import json
import astropy.units as u

from flask import Flask, request, jsonify
from flask_cors import CORS
from processing import (
    generate_spectrum,
    generate_background,
    process_spectrum,
    find_peaks
)
from processing_utils import param_check

app = Flask(__name__)
CORS(app)

try:
    with open("version.txt", "r") as f:
        version = f.read().strip()
        app.config["VERSION"] = version
except:
    print("No version file found")
    app.config["VERSION"] = "0.0.0"


@app.route("/", methods=["GET"])
def index():
    return (
        f"<h1 style='color:blue'>Raston Lab FTIR API - Version {app.config['VERSION']}</h1>"
    )


@app.route("/sample", methods=["POST"])
def sample():
    # Parse incoming JSON parameters.
    params = json.loads(request.data)

    # Verify the parameters.
    if not param_check(params):
        return jsonify(
            success=False,
            text="One of the given parameters was invalid. Please change some settings and try again.",
        )

    # Generate the raw spectrum.
    spectrum, error, message = generate_spectrum(params)
    if error:
        return jsonify(success=False, text=message)

    # Process the spectrum.
    processed_spectrum = process_spectrum(params, spectrum)
    x_value, y_value = processed_spectrum.get("transmittance_noslit")
    return jsonify(success=True, x=list(x_value), y=list(map(str, y_value)))


@app.route("/background", methods=["POST"])
def background():
    data = json.loads(request.data)

    if not param_check(data):
        return jsonify(
            success=False,
            text="One of the given parameters was invalid. Please change some settings and try again.",
        )

    spectrum, error, message = generate_spectrum(data)
    if error:
        return jsonify(success=False, text=message)

    try:
        background_spectrum = generate_background(spectrum)
    except Exception as e:
        return jsonify(success=False, text=f"Error generating background: {str(e)}")

    processed_spectrum = process_spectrum(data, background_spectrum)
    if processed_spectrum is None:
        return jsonify(success=False, text="Issue processing data")

    x_value, y_value = processed_spectrum.get("transmittance_noslit")
    return jsonify(success=True, x=list(x_value), y=list(map(str, y_value)))


@app.route("/find_peaks", methods=["POST"])
def handle_peaks():
    data = json.loads(request.data)
    peaks, error = find_peaks(data["x"], data["y"], float(data["threshold"]))
    if peaks:
        return jsonify(success=True, peaks=peaks, text=error)
    else:
        return jsonify(success=False, peaks=peaks, text=error)


# --- New test endpoint using hard-coded parameters ---
@app.route("/test", methods=["GET"])
def test():
    # Define a set of test parameters.
    test_params = {
        "beamsplitter": "AR_ZnSe",
        "detector": "MCT",
        "medium": "Vacuum",
        "mole": 1,
        "molecule": "CO",
        "pressure": 0.002,
        "resolution": 0.125,
        "scan": 100,
        "source": 1200,
        "waveMax": 5000,
        "waveMin": 1000,
        "window": "ZnSe",
        "zeroFill": 2
    }
    
    # Generate the raw spectrum.
    spectrum, error, message = generate_spectrum(test_params)
    if error:
        return jsonify(success=False, text=message)

    # Process the spectrum.
    processed_spectrum = process_spectrum(test_params, spectrum)
    x_value, y_value = processed_spectrum.get("transmittance_noslit")

    # Return the resulting spectrum data.
    return jsonify(success=True, x=list(x_value), y=list(map(str, y_value)))

@app.route("/test_clean", methods=["GET"])
def test_clean():
    # Override the processing module's global constants
    import processing
    processing.WAVEMIN = (2 * u.GHz).to(u.cm**-1, equivalencies=u.spectral()).value
    processing.WAVEMAX = (40 * u.GHz).to(u.cm**-1, equivalencies=u.spectral()).value

    # Define test parameters that match the desired range.
    test_params = {
        "beamsplitter": "AR_ZnSe",
        "detector": "MCT",
        "medium": "vacuum",
        "mole": 1,
        "molecule": "HC3N",
        "pressure": 0.0001,
        "resolution": 0.125,
        "scan": 100,
        "source": 1200,
        "waveMax": (40 * u.GHz).to(u.cm**-1, equivalencies=u.spectral()).value,
        "waveMin": (2 * u.GHz).to(u.cm**-1, equivalencies=u.spectral()).value,
        "window": "ZnSe",
        "zeroFill": 2
    }


    # Generate the raw spectrum using the new range.
    spectrum, error, message = generate_spectrum(test_params)
    if error:
        return jsonify(success=False, text=message)

    # Bypass the extra processing (i.e., do not call process_spectrum)
    x_value, y_value = spectrum.get("transmittance_noslit")

    # Return the data as JSON.
    return jsonify(success=True, x=list(x_value), y=list(map(str, y_value)))

# Set debug to False in production.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
