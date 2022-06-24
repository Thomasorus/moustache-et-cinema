import os
import requests
import shutil
from bs4 import BeautifulSoup

path = "movies"
url = "https://www.imdb.com/title/"

files = os.listdir(path)
sort = sorted(files)
sort.reverse()

filenames = []

for file in sort:
	filenames.append(file.replace(".txt", ""))



all_movies = []
menu = "<ul>"
for year in filenames:
	print(year)
	file = open(path + "/" + year + ".txt", "r")
	movies_ids = file.read().split()
	menu += "<li><a href='#" + year + "''>" + year + "</a></li>"

	movies = []
	for movie_id in movies_ids:
		link = url + movie_id
		res = requests.get(link)
		soup = BeautifulSoup(res.content, 'html.parser')
		title = soup.find('h1')
		print(str(title.contents[0]))
		image = soup.find('meta', property="og:image")
		plot = soup.find('meta', property="og:description")
		movie = {"title": str(title.contents[0]), "image": image.get("content"), "plot": plot.get("content"), "link": link}
		movies.append(movie)

	year_arr = {"year": str(year), "movies": movies}
	all_movies.append(year_arr)

menu += "</ul>"
content = ""
print(all_movies)
for item in all_movies:
	print(item["year"])
	content += "<section><div><div class='stick'><img class='moustache' src='images/" + item["year"] + ".png' aria-hidden='true'/>\n\t<h2 id=" + item["year"] + ">" + item["year"] + "</h2></div></div><div class='movies'>\n"
	for movie in item["movies"]:
		movie_string = "\t<article class='flow'>\n\t\t<img loading='lazy' src='" + movie["image"] + "'' alt='" + movie["title"] + "'/>\n\t\t<h3>" + movie["title"] + "</h3>\n\t\t<p>" + movie["plot"] + "</p>\n\t\t<a href='" + movie["link"] + "'>IMDB</a>\n\t</article>\n"
		content += movie_string
	content += "</div></section>"


start = open("partials/start.txt", "r")
start_width_menu = start.read().replace("MENU", menu)

end = open("partials/end.txt", "r")
complete = start_width_menu + content + end.read()
if os.path.exists("docs"):
    shutil.rmtree("docs")

# Make new folders
os.makedirs("docs")
f = open("docs/index.html", "w")
f.write(complete)
f.close()


assets = os.listdir("images")
os.makedirs("docs/images")
if assets:
	for asset in assets:
	    asset = os.path.join("images/", asset)
	    if os.path.isfile(asset):
	        shutil.copy(asset, "docs/images/")
else:
    print("No assets found!")


