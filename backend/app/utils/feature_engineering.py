import pandas as pd
# panda import for data manipulation
def create_features(df):
    #create features le historic river values lai  use garera flood risk prediction ma help garxa
    #rolling mean le river flow ko 7 din ko average calculate garxa jasko karan river ko sudden spike in water level le warning dinxa.
    df["rolling_flow_mean"] = (df["river_flow"].rolling(window=7).mean()
    )
    #rolling rainfall le past seven days ko rainfall ko mean liera flood risk calculation ma help garxa
    df["rolling_rainfall"] = (df["rainfall"].rolling(window=7).mean()
    )
    #month feature le monthly weather patterns ko effect capture garxa ani flood risk prediction ma help garxa
    df["month"] = df["date"].dt.month
    #Ecological threshold lai calculate garya. Formula is below. 15% of mean river flow is the formula.
    df["eco_threshold"] = (df["rolling_flow_mean"] * 0.15
    )
    #ecolocgiacal risk bhanya eco system lai maintain garna kati river flow chinxa herya
    # if the river flow is less than the ecological threshold, then ecological risk is 1 (high risk), otherwise it's 0 (low risk).
    df["ecological_risk"] = (df["river_flow"] < df["eco_threshold"]
    ).astype(int)
    # dropna le missing values lai drop garxa ani clean data return garxa which makes prediction highly accurate.
    df = df.dropna()
    # cleend data is retured.
    return df