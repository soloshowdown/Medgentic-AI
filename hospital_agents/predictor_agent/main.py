import NEST as nest

import requests

@nest.tool
def predict_patient_surge():
    data = requests.post("http://localhost:8010/run", json={"input": "fetch data"}).json()
    info = data["output"]

    pollution = info["pollution_index"]
    festival = info["festival"]
    temp = info["temperature"]

    score = 0
    if pollution > 150:
        score += 35
    if festival != "None":
        score += 40
    if temp > 30:
        score += 15

    surge_level = "LOW"
    if score >= 70:
        surge_level = "HIGH"
    elif score >= 40:
        surge_level = "MEDIUM"

    return {
        "surge_score": score,
        "surge_level": surge_level,
        "raw_data": info
    }

agent = nest.Agent(
    name="PredictionAgent",
    instructions="Predict patient surge based on environment + festival.",
    tools=[predict_patient_surge]
)

nest.run(agent, port=8020)
