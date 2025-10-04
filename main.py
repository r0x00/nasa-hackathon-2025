from flask import Flask, render_template, jsonify, request, abort
import xarray as xr
import pandas as pd
import earthaccess
from src.predictive_model import estimate, summarize

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


        # short names 
        # M2T1NXSLV, Aqua_AIRS_MODIS1km_IND, cru_monthly_mean_xdeg_1015
        
        # Earthdata search
        results = earthaccess.search_data(
            short_name="M2T1NXSLV",
            temporal=("1986-01-01", "1986-01-02"),
            polygon=[(-100, 40), (-110, 40), (-105, 38), (-100, 40)]
        )

        result_objects = earthaccess.open(results)

        ds = xr.open_mfdataset(result_objects)

        time_index = pd.to_datetime(ds['time'].values)

        result_data = ds['CLDPRS'].values # ds['CLDTMP'].values

        # result_data_values = result_data[:, lat_index, lon_index].values 
        result_data_values = result_data[:, 0, 0]

        # obs. time_index size must be equals to result_data_values size

        # print(f"Time index length: {len(time_index)}, {time_index.shape}")
        # print(f"Temperature values length: {len(result_data_values )}, {result_data_values.shape}")


        data_estimated = estimate({ 'ds': time_index, 'y': result_data_values })

        # summarize(historical_data)

        return jsonify(data_estimated.to_dict())



    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        abort(500, description="An unexpected error occurred")

