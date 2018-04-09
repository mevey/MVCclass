#!/usr/bin/env python

import flask
from flask import Response, request, send_file
import json
import sqlite3
import csv

# Create the application.
app = flask.Flask(__name__)


@app.route('/')
def index():
	args = {}

	format_ = request.args.get("format", "")
	speaker = request.args.get("name", "")
	year = request.args.get("year", "")
	party = request.args.get("party", None)
	state = request.args.get("state", None)
	quantile = request.args.get("quantile", None)
	committee = request.args.get("committee", "")

	connection = sqlite3.connect("mydatabase.sqlite") 
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()

	#Query that gets the records that match the query
	all_records_query = """SELECT
		person.full_name as fullname,
		person.honorific as honorific,
		speech.text as text,
		hearing.hearing_title as title,
		hearing.date as date,
		committee.committee_name as cname,
		committee.type as ctype,
		congressmember.party as party,
		congressmember.chamber as chamber,
		constituency.state_name as state,
		constituency.district as district,
		constituencycharacteristics.density_quintile as quantiles
		FROM
		hearing inner join speech on speech.hearing_id = hearing.hearing_id
		inner join speaker on speaker.speech_id = speech.speech_id
		inner join committee on committee.committee_id = hearing.committee_id
		inner join person on person.person_id = speaker.person_id
		inner join congressmember on congressmember.person_id  = person.person_id
		inner join constituency on congressmember.constituency_id = constituency.constituency_id
		inner join constituencycharacteristics on constituencycharacteristics.constituency_id = constituency.constituency_id

		%s %s;"""

	where_clause = ""
	where_clause_arr = []
	conditions_tuple = []
	if speaker or year or party or state or committee or quantile:
		if speaker:
			where_clause_arr.append(" person.full_name like ? ")
			conditions_tuple.append("%" + speaker + "%")
		if year:
			where_clause_arr.append(" hearing.date like ? " if len(year)>2 else "" )
			conditions_tuple.append("%" + year + "%")
		if party:
			where_clause_arr.append(" congressmember.party = ? " )
			conditions_tuple.append(party)
		if state:
			where_clause_arr.append(" constituency.state_name = ? " )
			conditions_tuple.append(state)
		if quantile:
			where_clause_arr.append(" constituencycharacteristics.density_quintile = ? ")
			conditions_tuple.append(quantile)
		if committee:
			where_clause_arr.append(" committee.committee_name like ? ")
			conditions_tuple.append("%" + committee + "%")
		where_clause = "where " + ("and".join(where_clause_arr))

	limit_statement = "limit 10" if format_ != "csv" else ""

	all_records_query = all_records_query % (where_clause, limit_statement)
	print(all_records_query)

	conditions_tuple = tuple(conditions_tuple)
	cursor.execute(all_records_query, conditions_tuple)
	records = cursor.fetchall()

	#Query to count the number of records
	count_query =  """SELECT count(*) as count
		FROM
		hearing inner join speech on speech.hearing_id = hearing.hearing_id
		inner join speaker on speaker.speech_id = speech.speech_id
		inner join committee on committee.committee_id = hearing.committee_id
		inner join person on person.person_id = speaker.person_id
		inner join congressmember on congressmember.person_id  = person.person_id
		inner join constituency on congressmember.constituency_id = constituency.constituency_id
		inner join constituencycharacteristics on constituencycharacteristics.constituency_id = constituency.constituency_id
		%s;"""

	count_query = count_query % (where_clause)
	cursor.execute(count_query, conditions_tuple)
	#There's a lot of if else going on here but I will send a better solution for you guys to work with
	no_of_records = cursor.fetchall()

	#Get committees
	committee_query = """
		SELECT DISTINCT(committee.committee_name) as name FROM committee;
	"""
	cursor.execute(committee_query)
	committees = cursor.fetchall()

	#states
	states_query = """
			SELECT DISTINCT(constituency.state_name) as name FROM constituency;
		"""
	cursor.execute(states_query)
	states = cursor.fetchall()

	connection.close()

	#Send the information back to the view
	#if the user specified csv send the data as a file for download else visualize the data on the web page
	if format_ == "csv": 
		return download_csv(records, "speeches_%s.csv" % (speaker.lower()))
	else:
		years = [x for x in range(2018, 1995, -1)]
		args['records'] = records
		args['no_of_records'] = no_of_records[0]['count']
		args['years'] = years
		args['committees'] = committees
		args['states'] = states
		args['selected_speaker'] = speaker
		args['selected_year'] = int(year) if year else None
		args['selected_state'] = state
		args['selected_party'] = party
		args['selected_committee'] = committee
		args['selected_quantile'] = quantile
		return flask.render_template('index.html', response = args)

########################################################################
# The following are helper functions. They do not have a @app.route decorator
########################################################################
def dictionary_factory(cursor, row):
	"""
	This function converts what we get back from the database to a dictionary
	"""
	d = {}
	for index, col in enumerate(cursor.description):
		d[col[0]] = row[index]
	return d

def download_csv(data, filename):
	"""
	Pass into this function, the data dictionary and the name of the file and it will create the csv file and send it to the view
	"""
	header = data[0].keys() #Data must have at least one record.
	with open('downloads/' + filename, "w+") as f:
		writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for row in data:
			writer.writerow(list(row.values()))
	
	#Push the file to the view
	return send_file('downloads/' + filename,
				 mimetype='text/csv',
				 attachment_filename=filename,
				 as_attachment=True)


if __name__ == '__main__':
	app.debug=True
	app.run()
