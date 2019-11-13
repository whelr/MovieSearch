import os
import csv
from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import Schema, ID, TEXT
from whoosh.query import *
from whoosh.qparser import QueryParser


app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
	print("Someone is at the home page.")
	return render_template('welcome_page.html')

@app.route('/my-link/')
def my_link():
	print('I got clicked!')
	return 'Click.'

@app.route('/results/', methods=['GET', 'POST'])
def results():
	global mySearcher
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args

	query = data.get('query')
	afterYear = data.get('afterYear')
	beforeYear = data.get('beforeYear')
	withDir = data.get('withDir')
	titles, year, director = mySearcher.search(query, afterYear, beforeYear, withDir)
	print("You searched for: " + query)
	print("The flags are: " + afterYear, beforeYear, withDir)
 
	return render_template('results.html', query=query, results=zip(titles, year, director))

class movieSearcher(object):

	def __init__(self):
		super(movieSearcher, self).__init__()

	def search(self, str, afterYear, beforeYear, withDir):
		# Open index to search, and create a Query Parser index to search name and descriptions.
		title = list()
		year = list()
		director = list()
		with self.indexer.searcher() as s:
			parser = QueryParser("title", schema=self.indexer.schema)
			q = parser.parse(str)
			# Use with so searcher is automatically closed afterwards.
			results = s.search(q, limit=None)
			# Get results of search with query, if no results state that.
			for r in results:
				# Take the results and make sure they fit the advanced search flags
				#if((int(r["year"]) > int(afterYear)) and (int(r["year"]) < int(beforeYear)) and (withDir in r["director"])):
				print(r["title"],r["year"],r["director"])
				title.append(r["title"])
				year.append(r["year"])
				director.append(r["director"])
			return title, year, director

	def index(self):
		schema = Schema(path=ID(stored=True), title=TEXT(stored=True), year=TEXT(stored=True), rated=TEXT(stored=True), director=TEXT(stored=True), actors=TEXT(stored=True), plot=TEXT(stored=True), imdb=TEXT(stored=True), poster=TEXT(stored=True), url=TEXT(stored=True))
		indexer = create_in("index", schema)
		writer = indexer.writer()

		with open('moviedata.csv') as csv_file:
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
	
	app.run(debug=True)
