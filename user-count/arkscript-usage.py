import requests
import dotenv
import os
import json
import datetime


dotenv.load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
output = "users.json"

search = "extension:ark let OR MUT NOT repo:ark-lang/ark NOT is:fork"
url_encoded = search.replace(":", "%3A").replace("*", "%2A").replace("/", "%2F").replace(" ", "+")
url = f"https://api.github.com/search/code?q={url_encoded}"

response = requests.request("GET", url, headers={'Authorization': f'Token {GITHUB_TOKEN}'})
data = response.json()

users = set()
repositories = set()

for item in data['items']:
    repo = item['repository']
    users.add(repo['owner']['login'])
    repositories.add(repo['full_name'])

if os.path.exists(output):
    with open(output) as f:
        data = json.loads(f.read())
else:
    data = {}

data[datetime.datetime.now().strftime("%Y-%m-%d")] = {
    'users': len(users),
    'repositories': len(repositories)
}

with open(output, 'w') as f:
    f.write(json.dumps(data))

