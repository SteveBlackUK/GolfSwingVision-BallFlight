# GolfSwingVision-BallFlight

# Based on https://github.com/cagrell/golfmodel

There are two endpints in use in this project:
1. the original goal - calculating ball flight based on simulator input data and returning landing distance, peak height as well as x,y,z and timestamp intervals for flight plotting

2. because I needed to use python for another math-heavy use case in the same project, there is also an ellipse calculation engine for calculating the best fit ellipses for x,y data passed in as an input

For the Ball Flight, if you run the project, you'll be able to hit an endpoint (@app.route('/calculate-ball-flight') by passing it a shot object with the required inputs (as seen in app.py).  


an example curl request:

curl --location --request POST 'http://127.0.0.1:5100/calculate-ball-flight' \
--header 'Content-Type: application/json' \
--data-raw '{
  "BallSpeed": 112.1218,
  "BackSpin": 3474.37,
  "SideSpin": -825,
  "HLA": 7.686317,
  "VLA": 19.85732,
}'
