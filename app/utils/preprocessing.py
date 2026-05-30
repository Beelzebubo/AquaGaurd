import pandas as pd

#pandas import for data manipulation
def load_datasets():
    # data set lai load garya. Melamchi koriver flow and weather data.
    water_df = pd.read_csv("data/melamchi_waterflow.csv")
    weather_df = pd.read_csv("data/melamchi_weather.csv")
# data cleaning garera merge garya . The cleaned data has 2 cloumns date and river_flow.
    water_df.columns = ["date", "river_flow"]
# weather data has 5 cloumns year, day_of_year, temperature, rainfall and humidity
# date columns lai create garna year and day_of_year use hunxa.
#year and day_of_year lai string ma convert garera data nikalya ani date format ma change garya. 
    weather_df.columns = [
        "year",
        "day_of_year",
        "temperature",
        "rainfall",
        "humidity"
    ]
# mathi kei comment ho date columns lai create garna year and day_of_year use hunxa string ma convert garera
    weather_df["date"] = pd.to_datetime(
        weather_df["year"].astype(str)
        + weather_df["day_of_year"].astype(str),
        format="%Y%j"
    )
# water data ko date column lai datetime format ma convert gareko. This is important for merging the datasets on date.
    water_df["date"] = pd.to_datetime(water_df["date"])
#date lai column ma merge garya. Inner join use garxa which means only dates that are present in both datasetes will be icludeed 
# in the final mergerd dataset.
    merged_df = pd.merge(
        water_df,
        weather_df,
        on="date",
        how="inner"
    )
# this returns the merged datasets which contains date, river_flow, temp, humidity adn rainfall
#this dataset will be used for feature engineering and model training for flood risk prediction
    return merged_df