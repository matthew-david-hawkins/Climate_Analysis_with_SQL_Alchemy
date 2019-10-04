################################################
# Overview

# /
# Home page.
# List all routes that are available.



# /api/v1.0/precipitation
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.



# /api/v1.0/stations
# Return a JSON list of stations from the dataset.



# /api/v1.0/tobs
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.



# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

################################################


import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

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
Measurement = Base.classes.measurement
Station = Base.classes.station

#Store global variables

session = Session(engine)

start_date_q = session.query(Measurement.date).order_by(Measurement.date).first()[0]
end_date_q = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

end_date = [int(x) for x in end_date_q.split('-')]
end_date = dt.date(end_date[0], end_date[1], end_date[2])

start_date = [int(x) for x in start_date_q.split('-')]
start_date = dt.date(start_date[0], start_date[1], start_date[2])

analysis_start = end_date - dt.timedelta(days=365)

print(f"{start_date}, {end_date}, {analysis_start}")
session.close()

def calc_temps(start_date, end_date):
# """TMIN, TAVG, and TMAX for a list of dates.

# Args:
#     start_date (string): A date string in the format %Y-%m-%d
#     end_date (string): A date string in the format %Y-%m-%d
    
# Returns:
#     TMIN, TAVE, and TMAX
# """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    # List all routes that are available.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all measurements
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    all_precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_precipitation.append(prcp_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all columns from Station
    sel = [
        Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation
        ]
    results = session.query(*sel).all()

    all_stations = []
    for id,station,name,latitude,longitude,elevation in results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    session.close()

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all columns from Station
    results = session.query(Measurement.tobs, Measurement.station, Measurement.date)\
                .filter(Measurement.date >= analysis_start).filter(Measurement.date <= end_date)

    all_temps = []
    for tobs,station,date in results:
        temp_dict = {}
        temp_dict["Observed Temperature"] = tobs
        temp_dict["station id"] = station
        temp_dict["date"] = date
        all_temps.append(temp_dict)

    session.close()

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def start_limit(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    def calc_temps(start_date, end_date):
    # """TMIN, TAVG, and TMAX for a list of dates.

    # Args:
    #     start_date (string): A date string in the format %Y-%m-%d
    #     end_date (string): A date string in the format %Y-%m-%d
        
    # Returns:
    #     TMIN, TAVE, and TMAX
    # """
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Calculate temperatures
    result = calc_temps(start_date, end_date)

    calc_dict = {}
    calc_dict["Min Temp"] = result[0][0]
    calc_dict["Avg Temp"] = result[0][1]
    calc_dict["Max Temp"] = result[0][2]

    session.close()

    return jsonify(calc_dict)

@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    def calc_temps(start_date, end_date):
    # """TMIN, TAVG, and TMAX for a list of dates.

    # Args:
    #     start_date (string): A date string in the format %Y-%m-%d
    #     end_date (string): A date string in the format %Y-%m-%d
        
    # Returns:
    #     TMIN, TAVE, and TMAX
    # """
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    start_date = [int(x) for x in start.split('-')]
    start_date = dt.date(start_date[0], start_date[1], start_date[2])

    end_date = [int(x) for x in end.split('-')]
    end_date = dt.date(end_date[0], end_date[1], end_date[2])

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Calculate temperatures
    result = calc_temps(start_date, end_date)

    calc_dict = {}
    calc_dict["Min Temp"] = result[0][0]
    calc_dict["Avg Temp"] = result[0][1]
    calc_dict["Max Temp"] = result[0][2]

    session.close()

    return jsonify(calc_dict)


if __name__ == '__main__':
    
    app.run(debug=True)
