import os
from flask import Flask, jsonify, request
import json
from flask_cors import CORS  # Add this import
from golf_ballistics import golf_ballistics
from mvee import mvee
import numpy as np
from scipy.linalg import eigh
from dotenv import load_dotenv
from datetime import datetime
from log import logger
from errors import register_error_handlers
from errors import MissingInputError
from errors import InvalidInputError
from errors import CannotFormEllipseError

load_dotenv()

app = Flask(__name__)
register_error_handlers(app)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 megabytes
flask_env = os.environ.get("FLASK_ENV", "development")

if flask_env == "development":
    CORS(app, resources={
        r"/*": {
            "origins": "http://localhost:3000",
            "methods": ["POST"]
        }
    })
else:
    CORS(app, resources={
        r"/*": {
            "origins": "https://golfswingvision.com",
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["POST"]
        }
    })


@app.route('/calculate-ball-flight', methods=['POST'])
def processData():
    try:
        # Parse the JSON data
        data = request.json

        # Check if required inputs are present
        required_inputs = ['BallSpeed', 'VLA', 'HLA', 'BackSpin', 'SideSpin']
        for input in required_inputs:
            if input not in data:
                raise MissingInputError(f"Missing required input: {input}")

        shot = data

        ball = golf_ballistics()

        # Extract relevant data from the shot object
        velocityMPH = float(shot['BallSpeed'])
        launch_angle_deg = float(shot['VLA'])
        off_center_angle_deg = float(shot['HLA'])
        backspin_rpm = float(shot['BackSpin'])
        sidespin_rpm = float(shot['SideSpin'])
        windspeed = 0
        windheading_deg = 180

        # Convert units
        velocity = velocityMPH * 0.44704

        # Call the initiate_hit method
        now = datetime.now()
        ball.initiate_hit(velocity, launch_angle_deg, off_center_angle_deg,
                          backspin_rpm, -sidespin_rpm, windspeed, windheading_deg)

        # Call the get_landingpos method
        x, y = ball.get_landingpos(velocity=velocity, launch_angle_deg=launch_angle_deg, off_center_angle_deg=off_center_angle_deg,
                                   backspin_rpm=backspin_rpm, sidespin_rpm=-sidespin_rpm, windspeed=windspeed, windheading_deg=windheading_deg)
        now2 = datetime.now()
        logger.info("total time for ball flight calc: " + str(now2 - now))
        # Convert output units back to yards
        x_yards, y_yards = x * 1.09361, y * 1.09361

        # Retrieve the maximum z-value from the simulation results
        max_z = ball.df_simres['z'].max()

        # Convert the maximum z-value from meters to yards
        max_z_yards = max_z * 1.09361

        def get_first_negative_z_index(df):
            for index, row in df.iterrows():
                if row['z'] < 0:
                    return index
            return -1

        # Find the index of the first row where z goes below zero
        first_negative_z_index = get_first_negative_z_index(ball.df_simres)

        # If there's a row with a negative z-value, include it and set its z value to 0
        if first_negative_z_index != -1:
            # ball.df_simres.at[first_negative_z_index, 'z'] = 0
            filtered_df_simres = ball.df_simres.iloc[:first_negative_z_index + 1]
        else:
            filtered_df_simres = ball.df_simres

        # Convert x, y, and z values from meters to yards
        filtered_df_simres.loc[:, ['x', 'y', 'z']
                               ] = filtered_df_simres.loc[:, ['x', 'y', 'z']] * 1.09361

        # Drop the 't', 'v_x', 'v_y', and 'v_z' columns
        filtered_df_simres = filtered_df_simres.drop(
            columns=['t', 'v_x', 'v_y', 'v_z'])

        # Convert the dataframe to a JSON object
        df_simres_json = filtered_df_simres.to_json(orient="records")

        # Format the result as a JSON object
        result = {
            "landing_position": {"x": x_yards, "y": y_yards},
            "peakHeight": max_z_yards,
            "trajectory_data": df_simres_json

        }
    except MissingInputError as e:
        logger.error(f"Missing input error: {e}")
        return jsonify({"error": str(e)}), e.status_code
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return jsonify({"error": "JSON decode error"}), 400
    except Exception as e:
        logger.error(f"Exception: {e}")
        return jsonify({"error": "Exception"}), 500
    return jsonify(result)


@app.route('/calculate-mvee', methods=['POST'])
def calculate_mvee():
    try:
        # Parse the JSON data
        data = request.json

        # Check if required inputs are present
        if 'points' not in data:
            raise MissingInputError("Missing required input: points")

        points_json = data['points']

        # Check if points is a list
        if not isinstance(points_json, list):
            raise InvalidInputError("Invalid input: points must be a list")

        # Check if each point is a list of two numbers
        for point in points_json:
            if not isinstance(point, list) or len(point) != 2:
                raise InvalidInputError(
                    "Invalid input: each point must be a list of two numbers")
            for value in point:
                if not isinstance(value, (int, float)):
                    raise InvalidInputError(
                        "Invalid input: each value in a point must be a number")

        # Convert the list of dictionaries to a numpy array
        points = np.array([[point[0], point[1]] for point in points_json])

        # Call the mvee function

        logger.info(f"Starting mvee calculation for {len(points)} points.")

        now = datetime.now()
        matrix_A, center = mvee(points, tol=1e-3)
        now2 = datetime.now()
        logger.info("total time for mvee calc : " + str(now2 - now))

        # Calculate the eigenvalues and eigenvectors of matrix A
        eigenvalues, eigenvectors = eigh(matrix_A)

        # Calculate the lengths of the semi-major (a) and semi-minor (b) axes
        a = 1 / np.sqrt(eigenvalues[0])
        b = 1 / np.sqrt(eigenvalues[1])

        # Calculate the rotation angle using the eigenvectors
        angle = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])

        # plot_ellipse_and_points(points, center, a, b, angle)

        # Format the result as a JSON object
        response = {
            "center": center.tolist(),
            "a": a,
            "b": b,
            "angle": angle,
        }

        return jsonify(response)

    except MissingInputError as e:
        logger.error(f"MissingInputError: {e}")
        raise e
    except InvalidInputError as e:
        logger.error(f"InvalidInputError: {e}")
        raise e
    except CannotFormEllipseError as e:
        logger.error(f"CannotFormEllipseError: {e}")
        raise e

    except Exception as e:
        logger.error(f"Exception: {e}")
        return jsonify({"error": "Exception"}), 500


if __name__ == "__main__":
    from os import environ
    from sys import argv

    if "FLASK_RUN_PORT" in environ:
        port = int(environ.get("FLASK_RUN_PORT"))
    elif len(argv) == 2:
        port = int(argv[1])
    else:
        port = 5100

    app.run(debug=True, port=port)
