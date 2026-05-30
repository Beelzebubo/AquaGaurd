def forecast_risk(
    rainfall,
    humidity,
    temperature
):
# Estimates future environmental risks based on current conditions.
# mainly rainfall, humidity, and temperature ko basis ma future ma flood risk kasto hunxa bhanne forecast garxa
# risk always stars at 0 and increases based on current conditions.    
    risk = 0
# low rainfall risk check
#rainfall 2mm bhanda kam = 20% risk increase since indicates drought, reduced river recharge(water cycle), low soil moisture etc.

    if rainfall < 2:
        risk += 20
# low humidity risk check
# humidity 40% bhanda kam = 20% risk increase since indicates dry conditions, mostly drought ko bela hunxa yesto.

    if humidity < 40:
        risk += 20
# high temperature risk check
# temperature 30°C bhanda besi = 20% risk increase since indicates heatwaves, dry atmospheric conditons,drought likelyhood.

    if temperature > 30:
        risk += 20
# risk level determine based on total risk score. 50% bhanda badi = high risk, 25% bhanda besi = moderate risk, and 25% bhanda kam = low risk.
    if risk >= 50:
        level = "High"

    elif risk >= 25:
        level = "Moderate"

    else:
        level = "Low"
# risk score and level return hunxa as a directory.
    return {
        "forecast_risk": level,
        "risk_score": risk
    }