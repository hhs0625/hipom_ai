import requests
import time
import json  

url = "https://pru1l7lvi6.execute-api.ap-northeast-2.amazonaws.com/dev/register_alarm"
headers = {
    "x-api-key": "P1fr2EBx5z6s0AAbdd8aQ52hD82ZFnmD3fExsaUM",
    "Content-Type": "application/json"
}

data = {
    "thing": "NavigationThing",
    "property": "Heading",
    "ship_number": "HDGRC7F_W",
    "priority": "WARNING",
    "m_code": "MNALAB",
    "desc": "description",
    "desc_detail": "description detail",
    "res": "res",
    "alarm_level": "point",
    "eas_group": "model version",
    "device": "model name",
    "area": "HiPOM",
    "state": "A"
}

try:
    with open("alarm_time.txt", "r") as file:
        alarm_times = file.readlines()
        for alarm_time in alarm_times:
            data["state"] = "A"
            data["alarm_time"] = alarm_time.strip()
            response = requests.post(url, json=data, headers=headers)
            print("Json:", json.dumps(data, indent=4))  
            print("Response Code:", response.status_code)
            print("Response Content:", response.json())
            time.sleep(1)  
except FileNotFoundError:
    print("Alarm time file not found.")
