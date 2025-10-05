from flask import Flask, render_template, jsonify, request, abort
import xarray as xr
import pandas as pd
import numpy as np
import earthaccess
from src.predictive_model import estimate, data_estimate_forecast
from datetime import date,timedelta, datetime

app = Flask(__name__)

# Front-end
@app.route('/')
def index():
    return render_template('index.html')

search_data={
    "M2T1NXSLV": [
        'CLDPRS', #cloud pressure
        'CLDTMP', #cloud temperature .
        # 'TQI', #total quality index (air)
        'U2M', #wind speed at 2 meters (east-west wind)
        'V2M', #wind speed at 2 meters (north-south wind)
        'TS', #sea surface temperature
        'PS', #surface pressure,
        'T250', #temperature at 250 hPa .
        'T2M',
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

        if not chosen_date or not lat or not long:
            abort(400, description="Missing required parameters")

        chosen_date_formated = datetime.strptime(chosen_date, "%Y-%m-%d")

        current_date = datetime.today().strftime("%Y-%m-%d")
        current_date = datetime.strptime(current_date, "%Y-%m-%d")

        if(current_date > chosen_date_formated or current_date == chosen_date_formated):
            abort(400, description="Chosen date must be greater than current date")

        
        first_date=chosen_date_formated - timedelta(days=10)
        last_date=chosen_date_formated

        timestamps_10_years = []

        for value in range(1, 10):
            one_year = timedelta(days=365 * value)

            timestamps_10_years.append({
                'first_date': first_date - one_year,
                'last_date': last_date - one_year
            })

        # Earthdata login
        auth = earthaccess.login(strategy="netrc")

        bounding_box = (float(long) - 1, float(lat) - 1, float(long) + 1, float(lat) + 1)

        # Earthdata search
        for key, value in search_data.items():
            short_name = key

            estimate_data_values = {}

            for time in timestamps_10_years:
                print(f"Requesting data {short_name} from {time['first_date']} to {time['last_date']}")

                results = earthaccess.search_data(
                    short_name=short_name,
                    temporal=(time['first_date'], time['last_date']),
                    bounding_box=bounding_box,
                )

                print("Results fetched!")

                result_objects = earthaccess.open(results)
                ds = xr.open_mfdataset(result_objects)

                time_index = pd.to_datetime(ds['time'].values)
                # print(f"Time index length: {len(time_index)}, {time_index.shape}")

                estimate_data_values['ds'] = time_index  

                subset_data = {}
                for v in value: 
                    print(f"Defining lazy subset for variable {v}")
                    
                    # obs. time_index size must be equals to result_data_values size
                    subset_var = ds[v].isel(lat=0, lon=0)

                    subset_data[v] = subset_var  

                computed_results = xr.Dataset(subset_data).compute() 

                for v in value: 
                    print(f"Formating result for variable {v}")

                    result_data_values = computed_results[v].values

                    if np.isnan(result_data_values).any(): 
                        continue

                    if v == 'T2M':
                        estimate_data_values['y'] = result_data_values
                    else:
                        estimate_data_values[v] = result_data_values

        last_history_date = estimate_data_values['ds'].max()
        periods = ((chosen_date_formated + timedelta(days=1)) - last_history_date).days
                        
        data_estimated = estimate(estimate_data_values, periods, chosen_date)

        return jsonify(data_estimated)


    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        error_code= e.code if e and type(e) is dict else 500
        error= str(e.description) if e and type(e) is dict  else "An unexpected error occurred"

        abort(error_code, description=error)

