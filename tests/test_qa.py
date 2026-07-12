import pytest
from backend.agents.qa_agent import qa_agent

def test_medical_qa_block():
    # Attempting to fetch diagnosis codes as Patient should block access
    result = qa_agent.answer_question(
        patient_id=1,
        question="What is my patient diagnosis code?",
        user_role="patient"
    )
    
    assert result["blocked"] is True
    assert "blocked" in result["answer"].lower() or "unauthorized" in result["answer"].lower()
