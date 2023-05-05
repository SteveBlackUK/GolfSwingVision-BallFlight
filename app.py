from flask import Flask, jsonify, request
import json
from flask_cors import CORS  # Add this import
from golf_ballistics import golf_ballistics

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS

@app.route('/calculate-ball-flight', methods=['POST'])
def processData():
    # Parse the JSON data
    data = request.json 

    shot = data

    ball = golf_ballistics()

    # Extract relevant data from the shot object
    velocityMPH = shot['BallSpeed']
    launch_angle_deg = shot['VLA']
    off_center_angle_deg = shot['HLA']
    backspin_rpm = shot['BackSpin']
    sidespin_rpm = shot['SideSpin']
    windspeed = 0
    windheading_deg = 180

    # Convert units
    velocity = velocityMPH * 0.44704

  # Call the initiate_hit method
    ball.initiate_hit(velocity, launch_angle_deg, off_center_angle_deg,
                    backspin_rpm, -sidespin_rpm, windspeed, windheading_deg)

    # Call the get_landingpos method
    x, y = ball.get_landingpos(velocity=velocity, launch_angle_deg=launch_angle_deg, off_center_angle_deg=off_center_angle_deg,
                    backspin_rpm=backspin_rpm, sidespin_rpm=-sidespin_rpm, windspeed=windspeed, windheading_deg=windheading_deg)

    # Convert output units back to yards
    x_yards, y_yards = x * 1.09361, y * 1.09361

    # Retrieve the maximum z-value from the simulation results
    max_z = ball.df_simres['z'].max()

    # Convert the maximum z-value from meters to yards
    max_z_yards = max_z * 1.09361

    # Filter the dataframe to keep only rows with non-negative z-values
    filtered_df_simres = ball.df_simres[ball.df_simres['z'] >= 0]

    # Convert x, y, and z values from meters to yards
    filtered_df_simres[['x', 'y', 'z']] = filtered_df_simres[['x', 'y', 'z']] * 1.09361

    # Drop the 't', 'v_x', 'v_y', and 'v_z' columns
    filtered_df_simres = filtered_df_simres.drop(columns=['t', 'v_x', 'v_y', 'v_z'])

    # Convert the dataframe to a JSON object
    df_simres_json = filtered_df_simres.to_json(orient="records")
    
    # Format the result as a JSON object
    result = {
        "landing_position": {"x": x_yards, "y": y_yards},
        "peakHeight": max_z_yards,
        "trajectory_data": df_simres_json

    }

    return jsonify(result)

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
