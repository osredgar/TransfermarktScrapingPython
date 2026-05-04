import requests

API_URL = "http://127.0.0.1:5000/"

try:
    # response = requests.get(API_URL + 'helloworld', timeout=5)
    response = requests.get(API_URL + "tm/8/2022", timeout=30)
    print(response.json())

except Exception as e:
    print({"error": f"{str(e)}"})
