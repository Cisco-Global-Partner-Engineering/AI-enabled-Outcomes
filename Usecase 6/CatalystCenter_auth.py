import requests
from requests.auth import HTTPBasicAuth
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pprint import pprint
import credentials

BASE_URL = 'https://sandboxdnac2.cisco.com'
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = credentials.DNAC_USERNAME
PASSWORD = credentials.DNAC_PASSWORD 


def get_data(uri,header=None, query=None):
    """
    Get data from Dnac using the uri and query provided
    
    params:   
            uri (str): uri to get data from
            header (dict): header to be passed to the uri (optional)
            query (dict): query to be passed to the uri (optional)
    
    Returns: 
            json: json response from Dnac
    """
    
    response = requests.post(BASE_URL + AUTH_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    token = response.json()['Token']
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    while True:
        url = BASE_URL + uri
        if(header):
            headers.update(header)
        response = requests.get(url, headers=headers, params=query, verify=False)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print("Exception raised : ",e)
                continue
        elif(response.status_code == 429):
            print("got response 429 from Dnac, retrying in 60 seconds..")
            time.sleep(60)
            continue
        else:
            print(response, response.text)
            continue

def post_data(uri, body=None):
    """
    Post data to Dnac using the uri and body provided

    params:
            uri (str): uri to post data to
            body (dict): body to be passed to the uri (optional)

    Returns:
            json: json response from Dnac
    """
    
    response = requests.post(BASE_URL + AUTH_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    token = response.json()['Token']
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    url = BASE_URL + uri
    response = requests.post(url,headers=headers,json=body,verify=False)
    if response.status_code == 202:
        return response.json()
    else:
        print("error while posting data : ", response, response.json())
        return False


def get_health():
    result = []
    #print("device-health : ")
    data_health = get_data(uri="/dna/intent/api/v1/device-health")['response']
    #pprint(data)
    #print("device-details : ")
    for item in data_health:
        query = {
            "searchBy": item["macAddress"],
            "identifier": "macAddress"
        }
        #print(query)
        data_detail = get_data(uri="/dna/intent/api/v1/device-detail", query=query)
        result.append({"device_health": item, "device_detail": data_detail})
    return result

if __name__ == "__main__":
    pprint(health())