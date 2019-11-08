import urllib.request
import sys
import json
from bs4 import BeautifulSoup

APIkey = "848c2ef8"
items = []
count = 0 #Create variable for counting items scraped.

for page in range(1, 101):
	print("Scraping page: %s" % (page))
	movies = urllib.request.urlopen("https://www.imdb.com/list/ls057823854/?sort=list_order,asc&st_dt=&mode=detail&page=%s" % (page))
	soup = BeautifulSoup(movies, 'html.parser')
	for a in soup.find_all('a', href=True):
		if a['href'].startswith('/title/'): #For each item url, if its a movie:
			movID = a['href'].split("/")[2]
			if movID not in items: #If not already stored, save item url to list of items.
				items.append(movID)

filename = "moviedata.csv"
f = open(filename,'w+') 
headers = "movID,title,year,rated,director,actors,plot,imdbRating,poster,url\n" #add actors later
f.write(headers)

for item in items:
	url = "http://www.omdbapi.com/?apikey=%s&i=%s" % (APIkey,item)

	try:
		page = urllib.request.urlopen(url) #check to ensure we can access the item url, if bad url, go to next item
	except Exception as e:
		print("error")
		continue
	
	body = BeautifulSoup(page, 'html.parser').getText()
	soup_dict = json.loads(body)

	title = (soup_dict['Title'].replace("\"", "\"\"")) 
	year = (soup_dict['Year'].replace("\"", "\"\""))
	rated = (soup_dict['Rated'].replace("\"", "\"\""))
	director = (soup_dict['Director'].replace("\"", "\"\""))
	actors = (soup_dict['Actors'].replace("\"", "\"\""))
	plot = (soup_dict['Plot'].replace("\"", "\"\""))
	imdbRating = (soup_dict['imdbRating'].replace("\"", "\"\""))
	poster = (soup_dict['Poster'].replace("\"", "\"\""))
	url = "https://www.imdb.com/title/%s" % (item)

	itemInfo = ("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"") % (item,title,year,rated,director,actors,plot,imdbRating,poster,url)
	f.write(itemInfo + '\n')

	count += 1

f.close()


print("Finished scraping %s movies." % (count))