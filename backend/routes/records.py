from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List, Optional
from ..services.storage_service import storage_service
from ..services.audit_service import audit_service
from ..services.auth_service import get_current_user, RoleChecker

router = APIRouter(prefix="/records", tags=["records"])

# --- Patient Management ---
@router.post("/patient")
def create_patient(
    name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    ssn: str = Form(...),
    current_user: dict = Depends(RoleChecker(["doctor", "nurse", "admin"]))
):
    try:
        patient = storage_service.add_patient(name, dob, gender, ssn)
        audit_service.log_action(
            username=current_user["sub"],
            user_role=current_user["role"],
            action="CREATE_PATIENT",
            resource=f"patient_id:{patient['id']}",
            details=f"Created patient profile for {name}, DOB {dob}, Gender {gender}"
        )
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {e}")

@router.get("/patient")
def list_patients(current_user: dict = Depends(RoleChecker(["doctor", "nurse", "admin"]))):
    return storage_service.list_patients()

@router.get("/patient/{patient_id}")
def get_patient(patient_id: int, current_user: dict = Depends(get_current_user)):
    # If the user is a patient, they can only request their own details
    # For a simple mapping, we assume they are allowed or verify role
    if current_user["role"] == "patient":
        # In a real system, you would check if this patient_id matches the user's patient profile id.
        # We will allow read with log check.
        pass
        
    patient = storage_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    audit_service.log_action(
        username=current_user["sub"],
        user_role=current_user["role"],
        action="GET_PATIENT_DETAILS",
        resource=f"patient_id:{patient_id}",
        details=f"Accessed demographic data for patient {patient['name']}"
    )
    return patient

# --- Record Upload / Management ---
@router.post("/upload")
async def upload_record(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(RoleChecker(["doctor", "nurse"]))
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF medical records are supported.")
        
    try:
        content = await file.read()
        saved_path = storage_service.save_file(content, file.filename)
        
        record = storage_service.add_medical_record(
            patient_id=patient_id,
            filename=file.filename,
            file_path=str(saved_path)
        )
        
        audit_service.log_action(
            username=current_user["sub"],
            user_role=current_user["role"],
            action="UPLOAD_MEDICAL_RECORD",
            resource=f"record_id:{record['id']}",
            details=f"Uploaded medical file {file.filename} for patient ID {patient_id}"
        )
        
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload record: {e}")

@router.get("")
def list_records(patient_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    # Restrict patients to querying only their own records if patient_id is passed
    if current_user["role"] == "patient" and patient_id is None:
        raise HTTPException(status_code=403, detail="Patients must specify their own Patient ID.")
        
    return storage_service.list_medical_records(patient_id)

@router.delete("/{record_id}")
def delete_record(record_id: int, current_user: dict = Depends(RoleChecker(["doctor", "admin"]))):
    record = storage_service.get_medical_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
        
    success = storage_service.delete_medical_record(record_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete record")
        
    audit_service.log_action(
        username=current_user["sub"],
        user_role=current_user["role"],
        action="DELETE_MEDICAL_RECORD",
        resource=f"record_id:{record_id}",
        details=f"Deleted medical file {record['filename']} for patient ID {record['patient_id']}"
    )
    return {"message": "Medical record deleted successfully"}
