from fastapi import APIRouter
from app.models.query import EvaluationRequest, EvaluationResponse
from app.services.evaluation import evaluation_service

router = APIRouter(prefix="/evaluate", tags=["evaluation"])

@router.post("", response_model=EvaluationResponse)
async def run_evaluation(req: EvaluationRequest = None):
    return evaluation_service.evaluate_benchmark(req.test_cases if req else None)
