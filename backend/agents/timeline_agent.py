from typing import List, Dict, Any
from datetime import datetime

class TimelineAgent:
    def build_timeline(self, extractions: List[Dict[str, Any]], records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes medical record extractions and compiles a sorted list of clinical events.
        """
        timeline = []
        
        # Map record_id to upload/document date
        record_dates = {rec["id"]: rec["upload_date"][:10] for rec in records}
        
        for ext in extractions:
            rec_id = ext.get("record_id")
            doc_date = record_dates.get(rec_id, "Unknown Date")
            
            # 1. Process Diagnoses
            diagnoses = ext.get("diagnoses") or []
            for diag in diagnoses:
                timeline.append({
                    "date": doc_date,
                    "type": "Diagnosis",
                    "event": f"Diagnosed with {diag.get('condition')} (ICD: {diag.get('icd10', 'Unknown')})",
                    "details": diag.get("condition")
                })
                
            # 2. Process Medications
            medications = ext.get("medications") or []
            for med in medications:
                timeline.append({
                    "date": doc_date,
                    "type": "Medication",
                    "event": f"Prescribed {med.get('name')} {med.get('dosage')} ({med.get('frequency')}) via {med.get('route')}",
                    "details": med.get("name")
                })
                
            # 3. Process Lab Results
            labs = ext.get("lab_results") or []
            for lab in labs:
                lab_date = lab.get("date") or doc_date
                timeline.append({
                    "date": lab_date,
                    "type": "Lab Result",
                    "event": f"Lab {lab.get('test_name')}: {lab.get('value')} (Ref: {lab.get('reference_range')})",
                    "details": f"{lab.get('test_name')} {lab.get('value')}"
                })
                
            # 4. Process Vital Signs
            vitals = ext.get("vital_signs") or []
            for vit in vitals:
                vit_date = vit.get("date") or doc_date
                timeline.append({
                    "date": vit_date,
                    "type": "Vital Sign",
                    "event": f"Recorded vital {vit.get('name')}: {vit.get('value')}",
                    "details": f"{vit.get('name')} {vit.get('value')}"
                })
                
        # Sort chronologically (oldest to newest)
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                return datetime.min

        timeline.sort(key=lambda x: parse_date(x["date"]))
        return timeline

timeline_agent = TimelineAgent()
