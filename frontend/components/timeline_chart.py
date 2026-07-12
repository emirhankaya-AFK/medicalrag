import streamlit as st
from typing import List, Dict, Any

def render_timeline(events: List[Dict[str, Any]]):
    if not events:
        st.info("No events found in timeline history.")
        return
        
    st.markdown("""
    <style>
        .timeline-container {
            border-left: 2px solid #E2E8F0;
            padding-left: 20px;
            margin-left: 10px;
            position: relative;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 20px;
        }
        .timeline-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            position: absolute;
            left: -27px;
            top: 4px;
            border: 2px solid white;
        }
        .dot-diagnosis { background-color: #EF4444; }
        .dot-medication { background-color: #F59E0B; }
        .dot-lab { background-color: #10B981; }
        .dot-vital { background-color: #8B5CF6; }
        
        .timeline-date {
            font-size: 0.85rem;
            font-weight: bold;
            color: #64748B;
            margin-bottom: 2px;
        }
        .timeline-content {
            background-color: white;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 10px 15px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .timeline-type {
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .type-diagnosis { color: #EF4444; }
        .type-medication { color: #D97706; }
        .type-lab { color: #059669; }
        .type-vital { color: #7C3AED; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for item in events:
        e_type = item.get("type", "General").lower().replace(" ", "-")
        dot_class = f"dot-diagnosis" if "diag" in e_type else f"dot-medication" if "med" in e_type else f"dot-lab" if "lab" in e_type else "dot-vital"
        type_class = f"type-diagnosis" if "diag" in e_type else f"type-medication" if "med" in e_type else f"type-lab" if "lab" in e_type else "type-vital"
        
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot {dot_class}"></div>
            <div class="timeline-date">{item.get('date')}</div>
            <div class="timeline-content">
                <div class="timeline-type {type_class}">{item.get('type')}</div>
                <div style="color: #1E293B; font-weight: 500;">{item.get('event')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
