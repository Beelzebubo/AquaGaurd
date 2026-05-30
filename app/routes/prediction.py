from fastapi import APIRouter

from app.services.model_service import predict_risk
# initalizes the router for prediction servies
router = APIRouter()


@router.post("/predict")
def predict(data: dict):

    features = [[
        data["temperature"],
        data["rainfall"],
        data["humidity"],
        data["river_flow"]
    ]]

    prediction = predict_risk(features)

    return {
        "predicted_risk": prediction
    }