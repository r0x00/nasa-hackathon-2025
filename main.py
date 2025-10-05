from flask import Flask, render_template, jsonify, request, abort
import xarray as xr
import pandas as pd
import numpy as np
import earthaccess
from src.predictive_model import estimate, summarize
from datetime import date,timedelta, datetime

app = Flask(__name__)

# Front-end
@app.route('/')
def index():
    return render_template('index.html')

search_data={
    "M2T1NXSLV": [
        'CLDPRS', #cloud pressure
        'CLDTMP', #cloud temperature
        'T10M', #temperature at 10 meters
        'T2M', #temperature at 2 meters
        'TQI', #total quality index (air)
        'U10M', #wind speed at 10 meters(east-west wind)
        'U2M', #wind speed at 2 meters (east-west wind)
        'V10M', #wind speed at 10 meters (north-south wind)
        'V2M', #wind speed at 2 meters (north-south wind)
        'TS', #sea surface temperature
        'PS', #surface pressure,
        'QV10M', #specific humidity at 10 meters
        'T250', #temperature at 250 hPa
        'T500', #temperature at 500 hPa
        'T850', #temperature at 850 hPa
        'SLP', #sea level pressure
        'T2MDEW' #dew point
    ]

    # short names 
    # M2T1NXSLV, Aqua_AIRS_MODIS1km_IND, cru_monthly_mean_xdeg_1015, PRECIP_SSMI_F13
}


# API
@app.route('/api/forecast', methods=['GET'])
def forecast():
    try:
        # query parameters
        chosen_date=request.args.get('chosen_date')

        lat=request.args.get('lat')
        long=request.args.get('long')

        current_date = date.today()
        current_date2 = datetime.strptime(chosen_date, "%Y-%d-%m")
        

        first_date= current_date2 - timedelta(days=7 * 1)
        last_date=current_date2

        print(f"First date: {first_date}, Last date: {last_date}")

        # Earthdata login
        auth = earthaccess.login(strategy="netrc")

        bounding_box = (float(long) - 1, float(lat) - 1, float(long) + 1, float(lat) + 1)

        # Earthdata search
        for key, value in search_data.items():
            short_name = key

            results = earthaccess.search_data(
                short_name=short_name,
                temporal=(first_date, last_date),
                bounding_box=bounding_box,
            )

            result_objects = earthaccess.open(results)

            ds = xr.open_mfdataset(result_objects)

            time_index = pd.to_datetime(ds['time'].values)
            # print(f"Time index length: {len(time_index)}, {time_index.shape}")

            estimate_data_values = {}
            estimate_data_values['ds'] = time_index    

            for v in value: 
                result_data = ds[v].values

                # obs. time_index size must be equals to result_data_values size
                result_data_values = result_data[:, 0, 0]

                if(np.isnan(result_data_values)).any(): 
                    continue

                # print(f"Temperature values length: {len(result_data )}, {result_data.shape}")

                if(v == 'T2M'):
                    estimate_data_values['y'] = result_data_values

                    continue

                estimate_data_values[v] = result_data_values


        data_estimated = estimate(estimate_data_values, chosen_date)

        data_estimated_to_especific_moment = data_estimated[data_estimated['ds'] == chosen_date]

        return jsonify(data_estimated_to_especific_moment.to_dict())



    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        abort(500, description="An unexpected error occurred")

