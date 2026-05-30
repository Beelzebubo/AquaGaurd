from fastapi import APIRouter

from app.services.compliance_engine import (
    evaluate_ifc_compliance
)

router = APIRouter()


@router.post("/compliance")
def compliance(data: dict):

    result = evaluate_ifc_compliance(
        data["current_flow"],
        data["eco_threshold"]
    )

    return result