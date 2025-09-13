import requests

# POST to generate and save the forecast
r_post = requests.post("http://127.0.0.1:5000/forecast")
print("POST Status:", r_post.status_code)
print(r_post.text)

# GET to fetch forecast for a specific day
r_get = requests.get("http://127.0.0.1:5000/forecast/2025-07-01")
print("GET Status:", r_get.status_code)
print(r_get.json())
