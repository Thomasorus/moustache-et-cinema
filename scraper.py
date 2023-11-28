import os
import json
import re
import requests
import shutil
from bs4 import BeautifulSoup
import string

cache_path = "cache.json"
path = "movies"
url = "https://www.imdb.com/title/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Accept-Language': 'fr'}

if not os.path.exists(cache_path):
    cache_file = open(cache_path, "x")
    cache_file.close()
cache_file = open(cache_path, "r")
cache_text = cache_file.read()
if cache_text.strip() == "":
    print("New cache")
    cache = False
else:
    cache = True
    cache_content = json.loads(cache_text)
cache_file.close()


files = os.listdir(path)
sort = sorted(files)
sort.reverse()

filenames = []

for file in sort:
    filenames.append(file.replace(".txt", ""))


all_movies = []
tmp_cache = []
menu = "<ul>"
for year in filenames:
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
        match = False
        if cache:
            for y in cache_content:
                for m in y["movies"]:
                    if movie_id == m["id"]:
                        print("Cached:", m["title"])
                        match = True
                        movies.append(m)
                        tmp_cache.append(m)
                        break

        if match == False:
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
            tmp_cache.append(movie)
        match = False
    year_arr = {"year": str(year), "movies": movies}
    all_movies.append(year_arr)



# Building HTML
print("\nBuilding HTML page")

menu += "</ul>"
content = ""
# print(all_movies)

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
if os.path.exists("docs"):
    shutil.rmtree("docs")

# Make new folders
os.makedirs("docs")
f = open("docs/index.html", "w", encoding="utf-8")
f.write(complete)
f.close()

cache_string = json.dumps(all_movies)
new_cache = open(cache_path, "w")
new_cache.write(cache_string)
new_cache.close()

assets = os.listdir("images")
os.makedirs("docs/images")
if assets:
    for asset in assets:
        asset = os.path.join("images/", asset)
        if os.path.isfile(asset):
            shutil.copy(asset, "docs/images/")
else:
    print("No assets found!")
