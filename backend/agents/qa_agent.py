import yaml
from pathlib import Path
from typing import Dict, Any
from ..services.llm_service import llm_service
from ..services.rag_service import rag_service

class MedicalQAAgent:
    def __init__(self):
        self.prompt_path = Path(__file__).resolve().parent.parent / "config" / "prompts.yaml"
        self.safety_path = Path(__file__).resolve().parent.parent / "config" / "safety_rules.yaml"
        self._load_configs()

    def _load_configs(self):
        try:
            with open(self.prompt_path, "r") as f:
                self.prompts = yaml.safe_load(f)
        except Exception:
            self.prompts = {}
            
        try:
            with open(self.safety_path, "r") as f:
                self.safety = yaml.safe_load(f)
        except Exception:
            self.safety = {}

    def answer_question(self, patient_id: int, question: str, user_role: str) -> Dict[str, Any]:
        """
        Interrogates medical database. Enforces clinical and HIPAA safety checks.
        """
        # HIPAA Safety Rule Check
        question_lower = question.lower()
        
        # Block diagnostic codes / billing keys request for Patient roles (HIPAA block)
        if user_role == "patient" and any(keyword in question_lower for keyword in ["diagnosis code", "icd code", "ssn", "billing"]):
            return {
                "answer": "Unauthorized access or restricted HIPAA data blocked. Patients cannot request billing or diagnostic codes directly. Please contact clinic administration.",
                "blocked": True,
                "citations": []
            }

        # Query vector store for patient chunks
        matches = rag_service.query_record_chunks(query_text=question, patient_id=patient_id, n_results=4)
        
        context_parts = []
        citations = []
        for idx, match in enumerate(matches):
            content = match.get("content", "")
            context_parts.append(f"Source {idx+1}:\n{content}")
            citations.append({
                "source_index": idx + 1,
                "snippet": content[:120] + "..."
            })
            
        context_str = "\n\n".join(context_parts)
        system_prompt = self.prompts.get("qa", "")
        
        # Format prompt
        prompt = system_prompt.format(context=context_str, question=question)
        
        # Generate answer
        answer = llm_service.generate_content(prompt)
        
        # Append medical warning disclaimer if interaction safety rule triggers
        disclaimer = ""
        safety_rules = self.safety.get("safety_rules", [])
        for rule in safety_rules:
            if rule.get("id") == "interaction_warning":
                disclaimer = "\n\n" + rule.get("disclaimer", "")
                break
                
        return {
            "answer": answer + disclaimer,
            "blocked": False,
            "citations": citations
        }

qa_agent = MedicalQAAgent()
