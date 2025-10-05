from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def estimate(data, periods=7, chosen_date="2025-10-6"): 
    df = pd.DataFrame(data)
    df = df.dropna()

    # Initialize Prophet model and fit the data
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality='auto', 
        daily_seasonality=False,
        seasonality_mode='additive',
        seasonality_prior_scale=10.0, 
        changepoint_prior_scale=0.05, 
    )

    forecast_variables=['ds', 'yhat', 'yhat_lower', 'yhat_upper']

    for key in data.keys():
        if key in ("y", "ds"): 
            continue

        forecast_variables.append(key)
        model.add_regressor(key)

    model.fit(df)

    # Create future dates (e.g., for the next 6 months)
    future = model.make_future_dataframe(
        periods=periods,
        freq='D'
    ) 

    for key in data.keys():
        if key in ("y", "ds"): 
            continue

        future[key] = np.concatenate([df[key].values, [np.nan] * periods])
        future[key] = np.concatenate([df[key].values, [0] * periods])

    # Predict future temperature
    forecast = model.predict(future)

    #forecast_data = forecast[forecast_variables]

    # Plot the forecast
    model.plot(forecast)
    model.plot_components(forecast)

    plt.show()


    result = data_estimate_forecast(forecast, chosen_date)

    return result

def data_estimate_forecast(data, chosen_date): 
    data['ds'] = pd.to_datetime(data['ds']) 

    # Filter data for the specific day
    specific_day_data = data[data['ds'].dt.date == pd.to_datetime(chosen_date).date()]

    temperature_forecast = specific_day_data[['yhat', 'yhat_lower', 'yhat_upper']].iloc[0]

    print(f"Forecasted Temperature: {temperature_forecast['yhat']} °C (Range: {temperature_forecast['yhat_lower']} - {temperature_forecast['yhat_upper']} °C)")

    cloud_temperature = None
    # Cloud Temperature (CLDTMP)
    if 'CLDTMP' in specific_day_data.columns:
        cloud_temperature = specific_day_data['CLDTMP'].iloc[0]
        print(f"Cloud Temperature: {cloud_temperature} °C")

    surface_pressure = None
    # Surface Pressure (PS)
    if 'PS' in specific_day_data.columns:
        surface_pressure = specific_day_data['PS'].iloc[0]
        print(f"Surface Pressure: {surface_pressure} hPa")

    t250_temperature = None
    # Temperature at 250hPa (T250)
    if 'T250' in specific_day_data.columns:
        t250_temperature = specific_day_data['T250'].iloc[0]
        print(f"Temperature at 250hPa: {t250_temperature} °C")

    windspeed = None
    windspeed_lower = None
    windspeed_upper = None
    # Windspeed (U2M, V2M)
    if 'U2M' in specific_day_data.columns and 'V2M' in specific_day_data.columns:
        # Wind speed calculation
        windspeed = np.sqrt(specific_day_data['U2M']**2 + specific_day_data['V2M']**2).iloc[0]
        print(f"Forecasted Wind Speed: {windspeed} m/s")

        if 'U2M_lower' in specific_day_data.columns and 'V2M_lower' in specific_day_data.columns:
            windspeed_lower = np.sqrt(specific_day_data['U2M_lower']**2 + specific_day_data['V2M_lower']**2).iloc[0]
        else:
            windspeed_lower = windspeed  # Default to forecast windspeed if lower bounds are missing

        if 'U2M_upper' in specific_day_data.columns and 'V2M_upper' in specific_day_data.columns:
            windspeed_upper = np.sqrt(specific_day_data['U2M_upper']**2 + specific_day_data['V2M_upper']**2).iloc[0]
        else:
            windspeed_upper = windspeed  # Default to forecast windspeed if upper bounds are missing

        print(f"Wind Speed Range: {windspeed_lower} - {windspeed_upper} m/s")

    snowfall_estimate = None
    # Snowfall Estimate (if temperature below 0°C and cloud temperature also low)
    if cloud_temperature is not None:
        snowfall_estimate = (temperature_forecast['yhat'] < 0) and (cloud_temperature < 0)  # Snow if both are below freezing
        print(f"Snowfall Estimate: {'Yes' if snowfall_estimate else 'No'}")

    # Rainfall Estimate (lower pressure and temperature contrast)
    rainfall_estimate = (surface_pressure < 1010) and ((t250_temperature - temperature_forecast['yhat']) < -10)
    print(f"Rainfall Estimate: {'Yes' if rainfall_estimate else 'No'}")

    # Extreme Weather Indices
    extreme_temperature = temperature_forecast['yhat'] > 35  # Example for extreme heat
    extreme_windspeed = windspeed > 20  # Example for extreme winds
    print(f"Extreme Temperature: {'Yes' if extreme_temperature else 'No'}")
    print(f"Extreme Windspeed: {'Yes' if extreme_windspeed else 'No'}")

    no_data="N/A"

    return {
        "temperature_forecast": f"{temperature_forecast['yhat']} °C" if temperature_forecast is not None else no_data,
        "cloud_temperature": f"{cloud_temperature} °C" if cloud_temperature is not None else no_data,
        "surface_pressure": f"{surface_pressure} hPa" if surface_pressure is not None else no_data,
        "t250_temperature": f"{t250_temperature} °C" if t250_temperature is not None else no_data,
        "windspeed": f"{windspeed} m/s" if windspeed is not None else no_data,
        "windspeed_lower": f"{windspeed_lower} m/s" if windspeed_lower is not None else no_data,
        "windspeed_upper": f"{windspeed_upper} m/s" if windspeed_upper is not None else no_data,
        "snowfall_estimate": f"{snowfall_estimate}" if snowfall_estimate is not None else no_data, 
        "rainfall_estimate": f"{rainfall_estimate}" if rainfall_estimate is not None else no_data,
        "extreme_temperature": f"{extreme_temperature}" if extreme_temperature is not None else no_data,
        "extreme_windspeed": f"{extreme_windspeed}" if extreme_windspeed is not None else no_data
    }
    

