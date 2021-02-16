import requests
import base64

headers = {'Authorization': 'Basic YWxsYWRpbjpvcGVuc2VzYW1l'}
url = "https://datasend.webpython.graders.eldf.ru/submissions/1/"
r = requests.post(url, headers=headers)
json_data = r.json()
print(json_data)
headers2 = {'Authorization': 'Basic Z2FsY2hvbm9rOmt0b3RhbWE='}
url2 = "https://datasend.webpython.graders.eldf.ru/submissions/super/duper/secret/"
r2 = requests.put(url2, headers=headers2)
json_data2 = r2.json()
print(json_data2)
