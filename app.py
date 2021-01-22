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

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Home Route
@app.route("/")
def home():
        return """<html>
                        <h1>Mir's Hawaii Climate App (Flask API)</h1>
                        <a href = "https://www.hawaiitourismauthority.org/" target = "_blank" ><img src="static\hawaii.png", alt="Hawaii Weather"/></a>
                        <h2>Precipitation analysis for last 12 months:</h2>
                                <ul>
                                <li><a href="/api/v1.0/precipitation" target = "_blank">/api/v1.0/precipitation</a></li>
                                <li><em>Ouptput format {date}:{prcp}</em></li>
                                </ul>
                        <h2>Station inventory:</h2>
                                <ul>
                                <li><a href="/api/v1.0/stations" target = "_blank">/api/v1.0/stations</a></li>
                                <li><em>Ouptput format {name}:{value}, {station}:{value}</em></li>
                                </ul>
                        <h2>Temperature Analysis for last 12 months for the most active station:</h2>
                                <ul>
                                <li><a href="/api/v1.0/tobs" target = "_blank">/api/v1.0/tobs</a></li>
                                <li><em>Ouptput format [date , temperature]</em></li>
                                </ul>
                        <h2>Temperature analysis from start date:</h2>
                                <ul>
                                <li><a href="/api/v1.0/2017-03-14" target = "_blank">/api/v1.0/2017-03-14</a></li>
                                <li><em>Ouptput format [date , min temperature, avg temperature, max temperature]</em></li>
                                </ul>
                        <h2>Temperature analysis between start date & end date:</h2>
                                <ul>
                                <li><a href="/api/v1.0/2017-08-01/2017-08-07" target = "_blank">/api/v1.0/2017-08-01/2017-08-07</a></li>
                                <li><em>Ouptput format [date , min temperature, avg temperature, max temperature]</em></li>
                                </ul>
                        <h2>Check out Hawaiian tourist attractions in the video below:</h2>
                        <iframe width="1280" height="720" src="https://www.youtube.com/embed/su3ejcIeVdo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        <p>Copyright &copy; 2020 - All Rights Reserved - (JK!)<a href="#">MirHomeWork</a></p>
                        <p>This page is used for homework purposes only!!!</p>
                </html>
                """

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
        # Create Session (Link) From Python to the DB
        session = Session(engine)
        
        # Find the most recent date in the data set.
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

        # Convert string date to date format
        last_dt = (dt.datetime.strptime(last_date, "%Y-%m-%d")).date()
        
        # Calculate the date one year from the last date in data set.
        one_year_ago = last_dt - dt.timedelta(days=365)
        
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
        # Close Session
        session.close()
        # Create a list of dictionaries with station info using for loop
        list_stations = []

        for st in stations_all:
                station_dict = {}

                station_dict["station"] = st[0]
                station_dict["name"] = st[1]

                list_stations.append(station_dict)        
        print("Server received request for 'stations' page...")
        # Return JSON List of Stations from the Dataset
        return jsonify(list_stations)

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

# Start Date Route
@app.route("/api/v1.0/<start>")
def start_from(start):
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

# Start-End Date Route
@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):
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

# Run the app
if __name__ == '__main__':
    app.run(debug=True)