import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.serializer import loads, dumps


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Assign the classes to variables called Station and Measurement
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """dates and temperature observations from the last yea"""
    # Query all tobs
    # Query date for the Measurment date 1 year before
    query_date = dt.date(2018, 6, 2) - dt.timedelta(days=365)
    results = session.query(Measurement.date,Measurement.tobs).\
              filter(Measurement.date > query_date).\
              order_by(Measurement.date).all()
    
    # Convert the query results to a Dictionary using date as the key and tobs as the value.
    # Return the json representation of your dictionary.
    tob_dict = {}
    for tob in results:
        tob_dict[tob.date] = tob.tobs
    return jsonify(tob_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.name).all()
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query tobs for prior year
    # Query date for the Measurment date 1 year before
    query_date = dt.date(2018, 6, 2) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
              filter(Measurement.date > query_date).all()

    # Create a list of temps
    # Return a json list of Temperature Observations (tobs) for the previous year
    all_tobs = []
    for tob in results:
        tob_dict = tob.tobs
        #tob_dict["tob"] = tob.tobs
        all_tobs.append(tob_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start dates"""

    results = session.query(func.min(Measurement.tobs).label("min"),func.avg(Measurement.tobs).label("avg"),func.max(Measurement.tobs).label("max")).\
              filter(Measurement.date > start).all()
    
    #given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    all_tobs = []
    for tob in results:
        tob_dict={}
        tob_dict["min"] = tob.min
        tob_dict["avg"] = tob.avg
        tob_dict["max"] = tob.max
        all_tobs.append(tob_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>/<end>")
def between_date(end,start):
    """calculate TMIN, TAVG, and TMAX for all dates start and end dates"""

    results = session.query(func.min(Measurement.tobs).label("min"),func.avg(Measurement.tobs).label("avg"),func.max(Measurement.tobs).label("max")).\
              filter(Measurement.date < end, Measurement.date > start).all()
    
    #given the start only, calculate TMIN, TAVG, and TMAX for all dates between start and end date
    all_tobs = []
    for tob in results:
        tob_dict={}
        tob_dict["min"] = tob.min
        tob_dict["avg"] = tob.avg
        tob_dict["max"] = tob.max
        all_tobs.append(tob_dict)

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)
