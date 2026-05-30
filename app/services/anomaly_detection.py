def detect_anomaly(
    rainfall,
    river_flow,
    rolling_flow
):
# River flow ko unusual behaviour detect garxa based on rainfall and river discharge(basically discharge means volume of water flowing through the river)
# ya 3 ta parameter use garya xa
# rainfall: current rainfall measurement
# river_flow: current river flow measurement
# rolling_flow: historical average river flow for the same period (rolling average)   

# logic: Heavy rainfall high xa tara river flow low xa bhane indication is:
# - water diversion (e.g., for irrigation or hydropower)
# - ecological stress (e.g., due to blockages or sedimentation)
# - potential measurement error (e.g., faulty sensors) and
# abnormal behaviour of hydrological system (e.g., landslide)

# tala ko line le yei anomaly condition detect garxa.
#if rainfall is high (>20mm) but river flow a lot lower (less than 50% of the historic average), tya anomaly xa bhanne indicate hunxa
#since rolling rate *0.5 garda 50% of historical average milxa. tuo condition check garca tala ko logic le

    if rainfall > 20 and river_flow < rolling_flow * 0.5:  # is satisfies condition then it return anomaly true and message indicating possible diversion or ecological stress
        return {
            "anomaly": True,
            "message": (
                "Possible diversion or ecological stress"
            )
        }
#if conditions normal xa ani no problem then anomaly lai false return garxa ani no anomaly detected message auxa.
    return {
        "anomaly": False,
        "message": "No anomaly detected"
    }