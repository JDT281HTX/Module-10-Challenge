# Import the dependencies.

from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################
database_path = "C:/Users/DonJa/Documents/Module 10 Challenge/Starter_Code/Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine) 

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
 
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last 12 months as JSON."""
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    precip_dict = {date: prcp for date, prcp in precip_data}
    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of all stations in the dataset."""
    stations_data = session.query(Station.station).all()
    stations_list = list(np.ravel(stations_data))
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the most active station over the last 12 months."""
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    tobs_list = [{date: tobs} for date, tobs in temperature_data]
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return TMIN, TAVG, and TMAX for dates >= start or between start and end."""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    else:
        results = session.query(*sel).filter(Measurement.date >= start).all()

    temps = list(np.ravel(results))
    return jsonify({"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]}) 

if __name__ == '__main__':
    app.run(debug=True)



