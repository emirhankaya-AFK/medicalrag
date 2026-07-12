import pytest
from backend.agents.extraction_agent import extraction_agent

def test_medical_extraction():
    mock_summary = "Patient diagnosed with Type 2 Diabetes (E11.9). Prescribed Metformin 500mg daily. Known allergy to Penicillin."
    result = extraction_agent.extract_medical_data(mock_summary)
    
    assert isinstance(result, dict)
    assert "diagnoses" in result
    assert "medications" in result
    assert "allergies" in result
