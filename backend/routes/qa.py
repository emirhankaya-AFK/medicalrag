from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..agents.qa_agent import qa_agent
from ..services.audit_service import audit_service
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/qa", tags=["qa"])

class MedicalQARequest(BaseModel):
    patient_id: int
    question: str

@router.post("")
def ask_question(request: MedicalQARequest, current_user: dict = Depends(get_current_user)):
    try:
        result = qa_agent.answer_question(
            patient_id=request.patient_id,
            question=request.question,
            user_role=current_user["role"]
        )
        
        # Log audit trail (Ensure query question is logged but sanitized of raw SSN/DOB patterns)
        audit_service.log_action(
            username=current_user["sub"],
            user_role=current_user["role"],
            action="ASK_QUESTION",
            resource=f"patient_id:{request.patient_id}",
            details=f"Asked: '{request.question}'. Blocked status: {result['blocked']}"
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer clinical query: {e}")
