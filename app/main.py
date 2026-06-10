# main.py is basically the glue that ties the code together
from fastapi import FastAPI
# FastAPI is imported
from fastapi.staticfiles import StaticFiles
# static files are imported 
from fastapi.middleware.cors import CORSMiddleware

# this call all the files in the routes folder basically. 
from app.routes.prediction import router as prediction_router
from app.routes.compliance import router as compliance_router
from app.routes.analytics import router as analytics_router
from app.routes.alerts import router as alerts_router

# ya hamle app ko title, description and version info deko basically.
app = FastAPI(
    title="PeakFlow Analytics",
    description=(
        "AI-Powered Hydropower ESG & IFC Compliance Monitoring"
    ),
    version="1.0.0"
)
# this is basically used for audio conversion from elevnlabs
# yesle audio directory lai define garxa
# CORS middleware to allow Streamlit frontend (port 8501) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory="audio"), name="audio")
# ya kk include garne bhanera lekhe ko ho 
# all the core logics from the file routes are included basically called(routed here). 
app.include_router(prediction_router)
app.include_router(compliance_router)
app.include_router(alerts_router)
app.include_router(analytics_router)

# app bhanne file project root folder ma xa bhanera dekhauxa.
# if all of the functions are running properly it gives message the API is running.
@app.get("/")
def root():
# ya bata message pathauxa
    return {
        "message": "PeakFlow Analytics API Running"
    }
