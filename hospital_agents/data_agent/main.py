import NEST as nest

import requests
from datetime import datetime

@nest.tool
def get_external_data(location="Mumbai"):
    # Pollution API (Breezometer or IQAir; here using dummy logic for hackathon)
    pollution_index = 180  # mock fallback value

    # Festival calendar (static for hackathon)
    today = datetime.today().strftime("%d-%m")
    festival_today = "None"
    festival_map = {
        "12-11": "Diwali",
        "25-03": "Holi",
        "07-09": "Ganesh Chaturthi"
    }
    if today in festival_map:
        festival_today = festival_map[today]

    # Weather (mock)
    temperature = 28
    humidity = 70

    return {
        "location": location,
        "pollution_index": pollution_index,
        "festival": festival_today,
        "temperature": temperature,
        "humidity": humidity
    }

agent = nest.Agent(
    name="DataAgent",
    instructions="Fetch environmental and festival data.",
    tools=[get_external_data]
)

nest.run(agent, port=8010)
