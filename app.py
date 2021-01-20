# Import Flask
from flask import Flask, jsonify

# Dependencies and Setup
import numpy as np
import datetime as dt

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool
import dateutil.parser as dparser

#################################################
# Database Setup
#################################################
# Reference: https://stackoverflow.com/questions/33055039/using-sqlalchemy-scoped-session-in-theading-thread
engine = create_engine("sqlite:///Resources/hawaii.sqlite", 
                       # connect_args={"check_same_thread": False}, 
                       # poolclass=StaticPool, 
                       echo=False)

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Home Route
@app.route("/")
def welcome():
        return """<html>
                        <h1>Hawaii Climate App (Flask API)</h1>
                        <img src="static\hawaii.png", alt="Hawaii Weather"/>
                        <p>Precipitation Analysis for last 12 months:</p>
                                <ul>
                                <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
                                </ul>
                        <p>Station Analysis:</p>
                                <ul>
                                <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
                                </ul>
                        <p>Temperature Analysis for last 12 months for the most active station:</p>
                                <ul>
                                <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
                                </ul>
                        <p>Start Day Analysis:</p>
                                <ul>
                                <li><a href="/api/v1.0/2017-03-14">/api/v1.0/2017-03-14</a></li>
                                </ul>
                        <p>Start & End Day Analysis:</p>
                                <ul>
                                <li><a href="/api/v1.0/2017-08-01/2017-08-07">/api/v1.0/2017-08-01/2017-08-07</a></li>
                                </ul>
                </html>
                """

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
        # Create Session (Link) From Python to the DB
        session = Session(engine)
        # Find the most recent date in the data set.
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        
        # Calculate the date one year from the last date in data set.
        one_year_ago = dparser.parse(last_date[0],fuzzy=True) - dt.timedelta(days=365)
        
        # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
        prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
        # Convert List of Tuples Into a Dictionary
        prcp_data_list = dict(prcp_data)
        # Close Session
        session.close()
        print("Server received request for 'precipitation' page...")
        # Return JSON Representation of Dictionary
        return jsonify(prcp_data_list)

# Station Route
@app.route("/api/v1.0/stations")
def stations():
        # Create Session (Link) From Python to the DB
        session = Session(engine)
        # Return a JSON List of Stations From the Dataset
        stations_all = session.query(Station.station, Station.name).distinct().all()
        # Convert List of Tuples Into Normal List
        station_list = list(stations_all)
        # Close Session
        session.close()
        print("Server received request for 'stations' page...")
        # Return JSON List of Stations from the Dataset
        return jsonify(station_list)

# TOBs Route
@app.route("/api/v1.0/tobs")
def tobs():
        # Create Session (Link) From Python to the DB
        session = Session(engine)
        # Find the most recent date in the data set.
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

        # Calculate the date one year from the last date in data set.
        one_year_ago = dparser.parse(last_date[0],fuzzy=True) - dt.timedelta(days=365)
        
        # Get the most active station.
        most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
        # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
        tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).\
                filter(Measurement.station == most_active_stations[0][0]).\
                order_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
        tobs_data_list = list(tobs_data)
        # Close Session
        session.close()
        print("Server received request for 'tobs' page...")
        # Return JSON List of Temperature Observations (tobs) for the Previous Year
        return jsonify(tobs_data_list)

# Start Day Route
@app.route("/api/v1.0/<start>")
def start_day(start):
        # Create Session (Link) From Python to the DB
        session = Session(engine)
        start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
        start_day_list = list(start_day)
        # Close Session
        session.close()
        print("Server received request for 'start' page...")
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
        return jsonify(start_day_list)

# Start-End Day Route
@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
        # Create Session (Link) From Python to the DB
        session = Session(engine)
        start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.date).all()
        # Convert List of Tuples Into Normal List
        start_end_day_list = list(start_end_day)
        # Close Session
        session.close()
        print("Server received request for 'start/end' page...")
        # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
        return jsonify(start_end_day_list)

# Define Main Behavior
if __name__ == '__main__':
    app.run(debug=True)