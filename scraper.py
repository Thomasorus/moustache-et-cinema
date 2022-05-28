import os
import requests
from bs4 import BeautifulSoup

path = "movies"
url = "https://www.imdb.com/title/"

files = os.listdir(path)
filenames = []

for file in files:
	filenames.append(file.replace(".txt", ""))

sort = sorted(files)
sort.reverse()

all_movies = []
for year in filenames:
	file = open(path + "/" + year + ".txt", "r")
	movies_ids = file.read().split()

	movies = []
	for movie_id in movies_ids:
		link = url + movie_id
		res = requests.get(link)
		soup = BeautifulSoup(res.content, 'html.parser')
		title = soup.find('h1')
		image = soup.find('meta', property="og:image")
		plot = soup.find('meta', property="og:description")
		movie = {"title": str(title.contents[0]), "image": image.get("content"), "plot": plot.get("content"), "link": link}
		movies.append(movie)

	year_arr = {"year": str(year), "movies": movies}
	all_movies.append(year_arr)

content = ""
for item in all_movies:
	content += "<section><div><div class='stick'><img class='moustache' src='images/" + item["year"] + ".png' aria-hidden='true'/>\n\t<h2>" + item["year"] + "</h2></div></div><div class='movies'>\n"
	for movie in item["movies"]:
		movie_string = "\t<article class='flow'>\n\t\t<img loading='lazy' src='" + movie["image"] + "'' alt='" + movie["title"] + "'/>\n\t\t<h3>" + movie["title"] + "</h3>\n\t\t<p>" + movie["plot"] + "</p>\n\t\t<a href='" + movie["link"] + "'>IMDB</a>\n\t</article>\n"
		content += movie_string
	content += "</div></section>"


start = open("partials/start.txt", "r")
end = open("partials/end.txt", "r")
complete = start.read() + content + end.read()
f = open("index.html", "w")
f.write(complete)
f.close()