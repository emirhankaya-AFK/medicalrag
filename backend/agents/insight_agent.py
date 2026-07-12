import yaml
from pathlib import Path
from typing import Dict, Any, List
from ..services.llm_service import llm_service

class InsightAgent:
    def __init__(self):
        self.prompt_path = Path(__file__).resolve().parent.parent / "config" / "prompts.yaml"
        self._load_prompts()

    def _load_prompts(self):
        try:
            with open(self.prompt_path, "r") as f:
                self.prompts = yaml.safe_load(f)
        except Exception:
            self.prompts = {}

    def generate_clinical_insights(self, extraction_data: List[Dict[str, Any]]) -> str:
        """
        Generates 3 bullet clinical insights from combined extraction logs.
        """
        if not extraction_data:
            return "No medical history available to summarize."
            
        # Format the extractions summary
        summary_log = []
        for idx, ext in enumerate(extraction_data):
            summary_log.append(f"Record #{idx+1}:")
            summary_log.append(f"  Diagnoses: {ext.get('diagnoses')}")
            summary_log.append(f"  Medications: {ext.get('medications')}")
            summary_log.append(f"  Labs: {ext.get('lab_results')}")
            summary_log.append(f"  Allergies: {ext.get('allergies')}")
            
        data_str = "\n".join(summary_log)
        system_prompt = self.prompts.get("insight", "")
        
        prompt = f"{system_prompt}\n\nPatient Data:\n{data_str}"
        
        return llm_service.generate_content(prompt)

insight_agent = InsightAgent()
