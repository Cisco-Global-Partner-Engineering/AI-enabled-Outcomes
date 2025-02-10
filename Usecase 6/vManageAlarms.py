import vManage_auth
from pprint import pprint
import json

def get_data():
    result = []
    query = {"query":{
        "field": "active",
        "type": "boolean",
        "value": ["true"],
        "operator": "equal"
    }}
    result = vManage_auth.get_data("/dataservice/alarms",query2=query)["data"]
    #pprint(result)
    print(f"Alarm data updated with length : {len(result)}")
    with open("alarms_sdwan.json", "w") as f:
        json.dump(result,f, indent=4)
    return result

if __name__ == "__main__":
    pprint(get_data())
