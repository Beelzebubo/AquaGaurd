def detect_anomaly(rainfall, river_flow, rolling_flow, eco_threshold=None):
    alerts = []

    # Existing: possible diversion or ecological stress
    if rainfall > 20 and river_flow < rolling_flow * 0.5:
        alerts.append("Possible diversion or ecological stress")

    if rainfall > 30 and river_flow > rolling_flow * 1.3:
        alerts.append("Heavy rainfall with rising river levels — monitor for flood conditions")

    if river_flow > rolling_flow * 1.5:
        alerts.append("River flow significantly above seasonal average — flood risk elevated")

    if rainfall > 50:
        alerts.append("Extreme rainfall event — potential flash flooding")

    if river_flow < rolling_flow * 0.3:
        alerts.append("Critically low river flow — severe ecological stress")

    if eco_threshold is not None:
        if river_flow > eco_threshold * 1.3:
            alerts.append("River flow exceeds ecological threshold — flooding likely")
        if river_flow < eco_threshold * 0.8:
            alerts.append("River flow below ecological threshold — environmental stress")

    return alerts
