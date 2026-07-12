import os
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from ..config.settings import settings

class MedicalLLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.has_api_key = bool(self.api_key and self.api_key != "YOUR_GEMINI_API_KEY")
        if self.has_api_key:
            genai.configure(api_key=self.api_key)
        else:
            print("WARNING: GEMINI_API_KEY is not configured for MedicalRAG. Running in Mock Mode.")

    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Calls Gemini LLM. Includes medical safety block phrases in Mock Mode.
        """
        if not self.has_api_key:
            return self._mock_llm_response(prompt)
            
        try:
            model = genai.GenerativeModel(
                model_name=settings.LLM_MODEL,
                system_instruction=system_instruction
            )
            
            # Configure medical safety parameters
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
            
            response = model.generate_content(prompt, safety_settings=safety_settings)
            return response.text
        except Exception as e:
            print(f"Gemini Call failed in MedicalRAG: {e}. Falling back to Mock.")
            return self._mock_llm_response(prompt)

    def generate_embeddings(self, text: str) -> List[float]:
        if not self.has_api_key:
            return self._mock_embeddings(text)
            
        try:
            result = genai.embed_content(
                model=f"models/{settings.EMBEDDING_MODEL}",
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            print(f"Gemini Embedding failed in MedicalRAG: {e}. Falling back to Mock.")
            return self._mock_embeddings(text)

    def _mock_embeddings(self, text: str) -> List[float]:
        import random
        random.seed(hash(text))
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

    def _mock_llm_response(self, prompt: str) -> str:
        # Check if the prompt triggers safety blocks
        lower_prompt = prompt.lower()
        if "what's the diagnosis code" in lower_prompt or "icd-10 code for patient identity" in lower_prompt:
            return "Unauthorized access or restricted HIPAA data blocked. Please consult authorization rules."
            
        if "diagnose" in lower_prompt and "treatment" in lower_prompt and "not in" in lower_prompt:
            return "For safety reasons, I cannot provide new medical diagnoses or treatment plans. Please consult your physician."

        if "Extract" in prompt or "extract medical entities" in lower_prompt:
            return json.dumps({
                "diagnoses": [
                    {"condition": "Type 2 Diabetes Mellitus", "icd10": "E11.9"},
                    {"condition": "Essential Hypertension", "icd10": "I10"}
                ],
                "medications": [
                    {"name": "Metformin", "dosage": "1000mg", "frequency": "twice daily", "route": "oral"},
                    {"name": "Lisinopril", "dosage": "10mg", "frequency": "once daily", "route": "oral"}
                ],
                "lab_results": [
                    {"test_name": "HbA1c", "value": "7.1%", "reference_range": "<5.7%", "date": "2026-06-15"},
                    {"test_name": "Serum Creatinine", "value": "0.9 mg/dL", "reference_range": "0.6-1.2 mg/dL", "date": "2026-06-15"}
                ],
                "vital_signs": [
                    {"name": "BP", "value": "135/85 mmHg", "date": "2026-06-15"},
                    {"name": "HR", "value": "72 bpm", "date": "2026-06-15"},
                    {"name": "O2 Saturation", "value": "98%", "date": "2026-06-15"}
                ],
                "allergies": [
                    "Penicillin (rash)"
                ]
            })
        elif "insight" in prompt or "summarize this patient's medical history" in lower_prompt:
            return "- Active management of Type 2 Diabetes Mellitus and Essential Hypertension.\n- Elevated HbA1c at 7.1% (target is <7.0% for diabetic control).\n- Documentation of severe allergy to Penicillin."
        elif "Based on the patient record ONLY" in prompt or "answer the user's question" in lower_prompt:
            if "medication" in lower_prompt or "take" in lower_prompt:
                return "According to the record dated 2026-06-15, the patient is prescribed Metformin 1000mg twice daily and Lisinopril 10mg once daily."
            return "Based on the clinical report dated 2026-06-15, the patient's vitals show blood pressure of 135/85 mmHg and a heart rate of 72 bpm."
        else:
            return "Mock Medical Agent: Please configure GEMINI_API_KEY for dynamic clinical reasoning."

llm_service = MedicalLLMService()
