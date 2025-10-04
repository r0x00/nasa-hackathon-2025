from flask import Flask, render_template, jsonify, request, abort
import xarray as xr
import pandas as pd
import earthaccess

app = Flask(__name__)

# Front-end
@app.route('/')
def index():
    return render_template('index.html')


# API
@app.route('/api/forecast', methods=['GET'])
def forecast():
    try:
        # query parameters
        first_date=request.args.get('first_date')
        last_date=request.args.get('last_date')
        lat=request.args.get('lat')
        long=request.args.get('long')

        # Earthdata login
        auth = earthaccess.login(strategy="netrc")

        # Map Url
        URL = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/thredds/dodsC/MERRA2_aggregation/M2T1NXSLV.5.12.4/M2T1NXSLV.5.12.4_Aggregation_1980.ncml'

        lat_slice = slice(41, 43)
        lon_slice = slice(-89, -87)
        time_slice = slice('1980-01-01', '1980-01-01') 

        # Access the THREDDS server ncml file, which will handle subset requests
        ds = xr.open_dataset(URL)

        # Send the subset request and stream data to the notebook using the bounding box and time slice
        ds_subset = ds.sel(lat=lat_slice,lon=lon_slice,time=time_slice)
        
        # Open the 2-meter temperature variable
        print(ds_subset['T2M'])

        return jsonify({'data': ds_subset['T2M'] })

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        abort(500, description="An unexpected error occurred")

