from fastapi import APIRouter, HTTPException, Depends
import json
from pathlib import Path
from ..services.storage_service import storage_service
from ..services.pdf_service import pdf_service
from ..services.rag_service import rag_service
from ..services.audit_service import audit_service
from ..services.auth_service import get_current_user, RoleChecker
from ..agents.extraction_agent import extraction_agent
from ..agents.timeline_agent import timeline_agent
from ..agents.insight_agent import insight_agent

router = APIRouter(prefix="/extraction", tags=["extraction"])

@router.post("/run/{record_id}")
def run_extraction(record_id: int, current_user: dict = Depends(RoleChecker(["doctor", "nurse"]))):
    rec = storage_service.get_medical_record(record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Medical record not found")
        
    try:
        # 1. Parse PDF and OCR if needed
        file_path = Path(rec["file_path"])
        parsing_result = pdf_service.extract_text(file_path)
        text = parsing_result["full_text"]
        
        # Index in ChromaDB
        rag_service.delete_record_chunks(record_id)
        rag_service.add_record_chunks(record_id, rec["patient_id"], text)
        
        # 2. Extract medical parameters
        extracted_data = extraction_agent.extract_medical_data(text)
        
        # 3. Generate individual report clinical insights
        insights = insight_agent.generate_clinical_insights([extracted_data])
        
        # Save to SQLite
        storage_service.add_extraction(
            record_id=record_id,
            diagnoses=json.dumps(extracted_data.get("diagnoses", [])),
            medications=json.dumps(extracted_data.get("medications", [])),
            lab_results=json.dumps(extracted_data.get("lab_results", [])),
            vital_signs=json.dumps(extracted_data.get("vital_signs", [])),
            allergies=json.dumps(extracted_data.get("allergies", [])),
            insights=insights
        )
        
        audit_service.log_action(
            username=current_user["sub"],
            user_role=current_user["role"],
            action="RUN_EXTRACTION",
            resource=f"record_id:{record_id}",
            details=f"Extracted medical data and clinical parameters from file: {rec['filename']}"
        )
        
        return {
            "status": "success",
            "record_id": record_id,
            "extraction": extracted_data,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

@router.get("/patient/{patient_id}/timeline")
def get_patient_timeline(patient_id: int, current_user: dict = Depends(get_current_user)):
    records = storage_service.list_medical_records(patient_id)
    extractions = []
    
    for rec in records:
        ext = storage_service.get_extraction(rec["id"])
        if ext:
            extractions.append({
                "record_id": rec["id"],
                "diagnoses": json.loads(ext["diagnoses"] or "[]"),
                "medications": json.loads(ext["medications"] or "[]"),
                "lab_results": json.loads(ext["lab_results"] or "[]"),
                "vital_signs": json.loads(ext["vital_signs"] or "[]"),
                "allergies": json.loads(ext["allergies"] or "[]")
            })
            
    timeline = timeline_agent.build_timeline(extractions, records)
    
    audit_service.log_action(
        username=current_user["sub"],
        user_role=current_user["role"],
        action="GET_PATIENT_TIMELINE",
        resource=f"patient_id:{patient_id}",
        details=f"Viewed chronological patient history timeline (total events: {len(timeline)})"
    )
    
    return timeline

@router.get("/patient/{patient_id}/insights")
def get_patient_insights(patient_id: int, current_user: dict = Depends(get_current_user)):
    records = storage_service.list_medical_records(patient_id)
    extractions = []
    
    for rec in records:
        ext = storage_service.get_extraction(rec["id"])
        if ext:
            extractions.append({
                "diagnoses": json.loads(ext["diagnoses"] or "[]"),
                "medications": json.loads(ext["medications"] or "[]"),
                "lab_results": json.loads(ext["lab_results"] or "[]"),
                "allergies": json.loads(ext["allergies"] or "[]")
            })
            
    insights = insight_agent.generate_clinical_insights(extractions)
    
    audit_service.log_action(
        username=current_user["sub"],
        user_role=current_user["role"],
        action="GET_PATIENT_INSIGHTS",
        resource=f"patient_id:{patient_id}",
        details="Generated aggregated clinical insights for patient medical records"
    )
    
    return {"insights": insights}
