import requests
import dotenv
import os
import datetime
import time


dotenv.load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OUTPUT_FILE = "data/users.csv"

search = 'extension:ark "let" OR "mut" NOT repo:ark-lang/ark NOT is:fork'
url_encoded = search.replace(":", "%3A").replace("*", "%2A").replace("/", "%2F").replace(" ", "+")
url_encoded = url_encoded.replace('"', "%22").replace("(", "%28").replace(")", "%29")
print(url_encoded)
url = f"https://api.github.com/search/code?q={url_encoded}"


def query(url: str):
    print(f"Fetching {url}...")
    response = requests.request("GET", url, headers={'Authorization': f'Token {GITHUB_TOKEN}'})
    data = response.json()
    return data, response.headers


def paginate(url: str):
    page, headers = query(url)
    data = [page]

    if "items" not in page:
        print(page)

    if 'rel="next"' in headers.get("Link", ""):
        urls = headers["Link"].split(",")
        next_url = ""
        for url in urls:
            if 'rel="next"' in url:
                # remove the <> around the url
                next_url = url.split(";")[0].strip()[1:-1]
                break

        if headers.get("X-RateLimit-Remaining", "0") == "0":
            reset_at = int(headers.get("X-RateLimit-Reset", f"{time.time():.0f}"))
            if reset_at > time.time():
                sleep_for = reset_at - time.time()
                print(f"Rate limited. Sleeping for {sleep_for:.3f} seconds")
                time.sleep(sleep_for)
        else:
            # sleep for 6 seconds to avoid hitting the rate limit too fast,
            # because we can only make 10 requests per minute to the API
            time.sleep(6)
        data += paginate(next_url)

    return data


def count(data):
    users = set()
    repositories = set()

    for page in data:
        for item in page['items']:
            repo = item['repository']
            users.add(repo['owner']['login'])
            repositories.add(repo['full_name'])

    print(users)
    print(repositories)

    return {
        'users': len(users),
        'repositories': len(repositories)
    }


def cache_results(pages):
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            data = [line for line in f.read().split("\n") if line]
            last = data[-1].split(", ")
    else:
        data = ["date, users, repositories"]
        last = []

    res = count(pages)
    # If we have a previous record and it is the same as what we just computed,
    # remove it. It will be replaced by our new record with the current date.
    # This will remove duplicates.
    if last != []:
        _, users, repos = last
        if int(users) == res["users"] and int(repos) == res["repositories"]:
            data.pop(-1)

    data.append(", ".join(str(e) for e in [
        datetime.datetime.now().strftime("%Y-%m-%d"),
        res["users"],
        res["repositories"]
    ]))

    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(data))


if __name__ == '__main__':
    pages = paginate(url)
    cache_results(pages)
