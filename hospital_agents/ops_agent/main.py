import NEST as nest

import requests

@nest.tool
def generate_hospital_plan():
    pred = requests.post("http://localhost:8020/run", json={"input": "predict"}).json()
    surge = pred["output"]

    level = surge["surge_level"]

    plan = {}

    if level == "LOW":
        plan = {
            "staff_required": "Normal staffing",
            "beds_to_prepare": 10,
            "med_supply": "Normal restock",
            "alert_level": "Green"
        }
    elif level == "MEDIUM":
        plan = {
            "staff_required": "Increase staff by 20%",
            "beds_to_prepare": 40,
            "med_supply": "Prepare emergency stock",
            "alert_level": "Yellow"
        }
    else:
        plan = {
            "staff_required": "Increase staff by 50%",
            "beds_to_prepare": 100,
            "med_supply": "Full emergency activation",
            "alert_level": "Red — High Surge Expected"
        }

    return {
        "prediction": surge,
        "hospital_plan": plan
    }

agent = nest.Agent(
    name="OpsAgent",
    instructions="Generate hospital management plans for festivals/pollution.",
    tools=[generate_hospital_plan]
)

nest.run(agent, port=8030, enable_tunnel=True)
