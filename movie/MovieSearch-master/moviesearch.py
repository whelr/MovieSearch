import os
import csv
from flask import Flask, render_template, url_for, request
from flask_bootstrap import Bootstrap
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import Schema, ID, TEXT
from whoosh.query import *
from whoosh import qparser
from whoosh import query
from whoosh.qparser import QueryParser
#from pagination import Pagination


app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
	print ('Home page')
	return render_template('welcome_page.html')

@app.route('/results/', methods=['GET', 'POST'])
def results():
	global mySearcher
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args

	query = data.get('query') + "~1"
	afterYear = data.get('afterYear')
	beforeYear = data.get('beforeYear')
	withDir = data.get('withDir')
	fuzzycheck = data.get('fuzzycheck')
	if(afterYear == ""):
		afterYear = 1
	if(beforeYear == ""):
		beforeYear = 99999
	movies = mySearcher.search(query, afterYear, beforeYear, withDir, fuzzycheck)
	r_size = sum(1 for _ in movies)

	page = request.args.get(get_page_parameter(), type=int, default=1)
	pagination = Pagination(page=page, total=r_size, record_name='movies', per_page=10)


#	return render_template('results.html', query=(query, afterYear, beforeYear, withDir), results=zip(poster, url, titles, year, director))
	return render_template('results.html',
                           movies=movies,
                           r_size=r_size,
                           pagination=pagination,
                           )
						   
@app.route('/options/', methods=['GET', 'POST'])
def options():
	return render_template('options.html')

class Movie:
    def __init__(self, poster, url, title, year, director):
        self.poster = poster
        self.url = url
        self.title = title
        self.year = year
        self.director = director

class movieSearcher(object):

	def __init__(self):
		super(movieSearcher, self).__init__()

	def search(self, str, afterYear, beforeYear, withDir, fuzzycheck):
		# Open index to search, and create a Query Parser index to search name and descriptions.
		if(fuzzycheck == "checked"):
			print("fuzzycheck is checked")

		movies = list()
		with self.indexer.searcher() as s:
			parser = qparser.QueryParser("title", schema=self.indexer.schema)
			parser.add_plugin(qparser.FuzzyTermPlugin())
			q = parser.parse(str)
			# Use with so searcher is automatically closed afterwards.
			results = s.search(q, limit=None)
			# Get results of search with query, if no results state that.
			if(len(results) == 0):
				results = s.documents()
			for r in results:
				# Take the results and make sure they fit the advanced search flags
				if((int(r["year"]) > int(afterYear)) and (int(r["year"]) < int(beforeYear)) and (withDir in r["director"])):
					pster = "https://lascrucesfilmfest.com/wp-content/uploads/2018/01/no-poster-available-737x1024.jpg"
					if(r["poster"] != "N/A"):
						pster = (r["poster"])
					movies.append(Movie(pster, r["url"], r["title"], r["year"], r["director"]))
			return movies

	def index(self):
		schema = Schema(path=ID(stored=True), title=TEXT(stored=True), year=TEXT(stored=True), rated=TEXT(stored=True), director=TEXT(stored=True), actors=TEXT(stored=True), plot=TEXT(stored=True), imdb=TEXT(stored=True), poster=TEXT(stored=True), url=TEXT(stored=True))
		indexer = create_in("index", schema)
		writer = indexer.writer()

# add [encoding='utf-8'] in line 100 after csv file if appears UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 5291: character maps to <undefined>
		with open('moviedata.csv', encoding='utf-8') as csv_file:
			# Load the csv file
			csv_reader = csv.reader(csv_file, delimiter=',')
			skip = 0
			for row in csv_reader:
				# Skip first row
				if(skip == 0):
					skip = 1
					continue
				# For each row in csv, add it as document with appropiate headers to index.
				writer.add_document(title=u"%s" % (row[1]), year=u"%s" % (row[2]), rated=u"%s" 
					% (row[3]), director=u"%s" % (row[4]), actors=u"%s" % (row[5]), plot=u"%s" 
					% (row[6]), imdb=u"%s" % (row[7]), poster=u"%s" % (row[8]), url=u"%s" % (row[9]))
		# Commit updates to index
		writer.commit()
		self.indexer = indexer


if __name__ == "__main__":
	global mySearcher
	mySearcher = movieSearcher()
	mySearcher.index()
	Bootstrap(app)
	app.run(debug=True)
