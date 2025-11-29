"""Ops Agent - Converts predicted surge into actionable resource plans."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any

from nest import Agent, tool
from utils.model_helpers import calculate_resource_requirements


@tool
def generate_resource_plan(load_prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Convert predicted loads into staffing and supply recommendations."""
    loads = load_prediction.get("loads", {})
    severity = load_prediction.get("combined_severity", 0.4)

    requirements = calculate_resource_requirements(loads)

    # Shift recommendations
    shift_plan = []
    if severity >= 0.7:
        shift_plan.append("Activate surge roster and call standby staff.")
        shift_plan.append("Extend ICU shifts to 12 hours with overlap.")
    elif severity >= 0.5:
        shift_plan.append("Add additional emergency shift for evening peak.")
    else:
        shift_plan.append("Maintain standard staffing with light on-call support.")

    # Supplies checklist
    checklist = [
        "Verify oxygen cylinder availability",
        "Check ventilator functionality",
        "Audit critical drug inventory",
        "Coordinate ambulance readiness",
    ]
    if loads.get("pharmacy", 0) > 400:
        checklist.append("Pre-pack common prescriptions to reduce pharmacy queue.")
    if loads.get("ventilator", 0) > 15:
        checklist.append("Prepare portable ventilator backups.")

    return {
        "resource_plan": {
            "requirements": requirements,
            "shift_plan": shift_plan,
            "checklist": checklist,
            "notes": [
                "Review plan with hospital operations team.",
                "Maintain coordination with municipal health authorities.",
            ],
        }
    }


ops_agent = Agent(
    name="OpsAgent",
    instructions=(
        "Converts predicted hospital surge numbers into detailed staffing, bed, "
        "ICU, and supply plans with operational checklists."
    ),
    tools=[generate_resource_plan],
)

if __name__ == "__main__":
    from nest import run

    run(ops_agent, port=8015)

