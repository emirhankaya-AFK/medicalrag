import yaml
import json
from pathlib import Path
from typing import Dict, Any
from ..services.llm_service import llm_service

class MedicalExtractionAgent:
    def __init__(self):
        self.prompt_path = Path(__file__).resolve().parent.parent / "config" / "prompts.yaml"
        self._load_prompts()

    def _load_prompts(self):
        try:
            with open(self.prompt_path, "r") as f:
                self.prompts = yaml.safe_load(f)
        except Exception as e:
            self.prompts = {}

    def extract_medical_data(self, text: str) -> Dict[str, Any]:
        """
        Calls Gemini to extract medical information in structured format.
        """
        system_prompt = self.prompts.get("extraction", "")
        prompt = f"{system_prompt}\n\nClinical Text:\n{text[:30000]}"
        
        response_text = llm_service.generate_content(prompt)
        return self._parse_json_object(response_text)

    def _parse_json_object(self, text: str) -> Dict[str, Any]:
        try:
            cleaned = text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                cleaned = cleaned[start:end+1]
                
            return json.loads(cleaned)
        except Exception as e:
            print(f"Failed to parse medical JSON object: {e}. Raw: {text}")
            return {
                "diagnoses": [],
                "medications": [],
                "lab_results": [],
                "vital_signs": [],
                "allergies": []
            }

extraction_agent = MedicalExtractionAgent()
