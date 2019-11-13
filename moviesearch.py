import os
import csv
import whoosh
from whoosh import index
from whoosh.fields import Schema, ID, TEXT
from whoosh.query import *
from whoosh.qparser import QueryParser

def init_session():
	# Initiate session, welcome user and state what database contains.
	print("Welcome to Movie Search.")
	# Start never ending while loop to allow "infinite" searches.
	while(True):
		# Prompt user for search query input
		entered = input("\nSearch: ")
		if(entered == "q"):
			# If they enter q, let them quit the program
			print("Quitting...")
			exit()
		# check for advanced search filter flags
		afterYear = get_afterYear(entered)
		beforeYear = get_beforeYear(entered)
		withDir = get_withDir(entered)
		# Remove filter flags from query before searching.
		filtered = (' '.join(tuple(word for word in entered.split() if not ( (word.startswith('afterYear:') or 
			(word.startswith("beforeYear:") or (word.startswith("withDir:"))))))))
		search(filtered, afterYear, beforeYear, withDir)

def get_afterYear(str):
	# Default limit is 10
	year = 0
	words = str.split()
	# Split up the input, check for result flag and splice out desired limit
	for word in words:
		if(word.startswith("afterYear:")):
			year = int(word.split(":")[1])
	return(year)

def get_beforeYear(str):
	# Default before the year 9999, we are future proof baby!
	year = 9999
	words = str.split()
	# Split up the input, check for result flag and splice out desired year
	for word in words:
		if(word.startswith("beforeYear:")):
			year = int(word.split(":")[1])
	return(year)

def get_withDir(str):
	# Default director is none
	director = ""
	words = str.split()
	# Split up the input, check for result flag and splice out desired director
	for word in words:
		if(word.startswith("withDir:")):
			director = (word.split(":")[1])
	return(director)

def search(str, afterYear, beforeYear, withDir):
	# Open index to search, and create a Query Parser index to search name and descriptions.
	ix = index.open_dir("index")
	parser = QueryParser("title", ix.schema)
	# Have the parser parse the input string
	q = parser.parse(str)
	with ix.searcher() as s:
		# Use with so searcher is automatically closed afterwards.
		results = s.search(q)
		# Get results of search with query, if no results state that.
		if(len(results) == 0):
			print("No movies for \"%s\"." % str)
			return
		print("Showing movies for \"%s\"." % str)
		for r in results:
			# Take the results and make sure they fit the advanced search flags
			if((int(r["year"]) > afterYear) and (int(r["year"]) < beforeYear) and (withDir in r["director"])):
				print(r["title"],r["year"],r["director"])

def load_index(dir):
	# Check if the index directory exists, if not create it.
	if not (index.exists_in(dir)):
		try:
			os.mkdir("index")
		except OSError:
			print("Error creating index.")

	# Create new index and open it as writer every load. It is nearly instant with our dataset.
	ix = index.create_in(dir, schema = get_schema())
	writer = ix.writer()

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

def get_schema():
	return Schema(path=ID(stored=True), title=TEXT(stored=True), year=TEXT(stored=True), 
		rated=TEXT(stored=True), director=TEXT(stored=True), actors=TEXT(stored=True),
		plot=TEXT(stored=True), imdb=TEXT(stored=True), poster=TEXT(stored=True), url=TEXT(stored=True))

if __name__ == "__main__":
	# Program Launched, load index and initiate session.
	# load_index("index") 
	init_session()
