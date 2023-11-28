import os
import json
import re
import requests
import shutil
from bs4 import BeautifulSoup
import string

# Config
path = "movies"
cache_path = "cache"
url = "https://www.imdb.com/title/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Accept-Language': 'fr'}

# Years
years = []
files = os.listdir(path)
files_sorted = sorted(files)
files_sorted.reverse()
for file in files_sorted:
    years.append(file.replace(".txt", ""))

# Movies
all_movies = []
menu = "<ul>"
for year in years:
    print("\n" + year)
    file = open(path + "/" + year + ".txt", "r")
    movies_ids = file.read().split("\n")
    menu += "<li><a href=\"#" + year + "\">" + year + "</a></li>"
    movies = []
    for movie_infos in movies_ids:
        if movie_infos == "":
            continue
        movie_arr = re.split(" ", movie_infos)
        movie_id = movie_arr[0]
        if len(movie_arr) >= 2:
            podium = movie_arr[1]
        else:
            podium = ""
        if os.path.exists("cache/" + movie_id + ".json"):
            cache_file = open("cache/" + movie_id + ".json", "r")
            cache_content = cache_file.read()
            cache_array = json.loads(cache_content)
            cache_file.close()
            print("Cached:", cache_array["title"])
            movies.append(cache_array)
        else:
            link = url + movie_id
            res = requests.get(link, headers=headers)
            soup = BeautifulSoup(res.content, "html.parser")
            title = soup.find("h1").get_text()
            print("Fetch:", str(title))
            image = soup.find("meta", property="og:image")
            plot = soup.find("meta", property="twitter:image:alt")
            movie = {
                "id": movie_id,
                "title": str(title),
                "image": image.get("content"),
                "plot": plot.get("content"),
                "link": link,
                "year": year,
                "podium": podium,
            }
            movies.append(movie)
            cache_json = json.dumps(movie)
            if not os.path.exists("cache"):
                os.makedirs("cache")
            cache_tmp = open("cache/" + movie_id + ".json", "w")
            cache_tmp.write(cache_json)
            cache_tmp.close()
    year_arr = {"year": str(year), "movies": movies}
    all_movies.append(year_arr)

# Building HTML
print("\nBuilding HTML page")
menu += "</ul>"
content = ""
for item in all_movies:
    print(item["year"])
    content += (
        "\n    <section>\n      <div>\n        <div class=\"stick\"><img class=\"moustache\" src=\"images/"
        + item["year"]
        + ".png\" aria-hidden=\"true\" /><h2 id="
        + item["year"]
        + ">"
        + item["year"]
        + "</h2></div>\n      </div>\n      <div class=\"movies\">\n"
    )
    for movie in item["movies"]:
        movie_string = (
            "        <article class=\"flow "
            + movie["podium"]
            + "\" id=\""
            + movie["id"]
            + "\">\n          <img loading=\"lazy\" src=\""
            + movie["image"]
            + "\" alt=\""
            + movie["title"]
            + "\" />\n          <h3>"
            + movie["title"]
            + "</h3>\n          <p>"
            + movie["plot"]
            + "</p>\n          <a href=\""
            + movie["link"]
            + "\">IMDB</a>\n        </article>\n"
        )
        content += movie_string
    content += "      </div>\n    </section>\n"
start = open("partials/start.html", "r", encoding="utf-8")
start_width_menu = start.read().replace("MENU", menu)
end = open("partials/end.html", "r", encoding="utf-8")
complete = start_width_menu + content + end.read()

# Create output
if os.path.exists("docs"):
    shutil.rmtree("docs")
os.makedirs("docs")
f = open("docs/index.html", "w", encoding="utf-8")
f.write(complete)
f.close()

# Copy assets
assets = os.listdir("images")
os.makedirs("docs/images")
if assets:
    for asset in assets:
        asset = os.path.join("images/", asset)
        if os.path.isfile(asset):
            shutil.copy(asset, "docs/images/")
else:
    print("No assets found!")
