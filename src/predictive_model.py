from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt


def estimate(data): 
    df = pd.DataFrame(data)


    # Prepare the data in the right format for Prophet
    df_prophet = df
    
    # df[['ds', 'y']].rename(columns={'date': 'ds', 'temperature': 'y'})

    # Initialize Prophet model and fit the data
    model = Prophet(yearly_seasonality=True)
    model.fit(df_prophet)

    # Create future dates (e.g., for the next 6 months)
    future = model.make_future_dataframe(periods=180)  # 180 days = ~6 months

    # Predict future temperature
    forecast = model.predict(future)

    forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    # Plot the forecast
    model.plot(forecast)
    model.plot_components(forecast)

    plt.show()

    return forecast_data



def summarize(data): 
    df = pd.DataFrame(data)

    # Convert 'date' column to datetime format
    df["date"] = pd.to_datetime(df["date"])

    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["temperature"], label="Temperature (°C)")
    plt.plot(df["date"], df["windspeed"], label="Wind Speed (m/s)")
    plt.plot(df["date"], df["rain"], label="Rainfall (mm)")
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("Weather Data Trends")
    plt.show()

    

