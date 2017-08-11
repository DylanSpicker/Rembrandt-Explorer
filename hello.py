from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
import json
import twitter
import time
from watson_developer_cloud import DiscoveryV1

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

# Set-up the Watson Developer Cloud - Discovery API;
discovery = DiscoveryV1(
  username='4163a3be-2d26-48f2-9cc0-7f605b0b6031',
  password='Faz00kGerZpg',
  version='2017-06-25'
)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('PORT', 8080))
# debug = True
debug = False

@app.route('/')
@app.route('/<int:file_id>')
def home(file_id=1):
    infile = open('json_content/json_corpus_'+str(file_id)+'.json', 'r')
    json_content = json.load(infile)
    infile.close()

    return render_template('individual.html',content_json=json_content)

@app.route('/discovery',methods=['GET'])
def discoveryHome():
    return render_template('discovery.html')

@app.route('/discovery', methods=['POST'])
def discoveryQuery():
    environment_id = "faf1b077-e582-45a9-9769-dba02866082f"
    collection_id = "403fa63f-b5d6-4639-b500-9bdce8bdc2a5"
    sentiment = ""
    concept = ""
    keyword = ""
    entity = ""
    
    if int(request.form['sentiment_restriction']) != 0:
        # Filter specified for Sentiment
        if int(request.form['sentiment_restriction']) == 1:
            sentiment = "enriched_text.docSentiment.type:positive,"
        elif int(request.form['sentiment_restriction']) == 2:
            sentiment = "enriched_text.docSentiment.type:negative,"
        elif int(request.form['sentiment_restriction']) == 3:
            sentiment = "enriched_text.docSentiment.type:neutral,"
    
    if len(request.form['concepts']) != 0:
        concept = "enriched_text.concepts.text:"+request.form['concepts']
        # Concept Filters Specified
        # concepts = request.form['concepts'].split(',')

        # for c in concepts:
            # concept += 'concepts.text:\"'+c.strip()+'\",'
    
    if len(request.form['keywords']) != 0:
        keyword = "enriched_text.keywords.text:"+request.form['keywords']
        # Concept Filters Specified
        # keywords = request.form['keywords'].split(',')

        # for c in keywords:
            # keyword += 'keywords.text:\"'+c.strip()+'\",'
    
    if len(request.form['entities']) != 0:
        entity = "enriched_text.entities.text:"+request.form['entities']
        # Concept Filters Specified
        # entities = request.form['entities'].split(',')

        # for c in entities:
        #     entity += 'entities.text:\"'+c.strip()+'\",'
    


    filter_str = sentiment[:-1]

    if len(concept) > 0:
        if (len(filter_str) > 0):
            filter_str += ","
        filter_str += concept 

    if len(keyword) > 0:
        if (len(filter_str) > 0):
            filter_str += ","
        filter_str += keyword


    if len(entity) > 0:
        if (len(filter_str) > 0):
            filter_str += ","
        filter_str += entity

    # print(filter_str)

    qopts = {
        'natural_language_query': request.form['natural_language_query'],
        'filter': filter_str,
        'passages': True,
        'highlight': True
    }    
    
    query = discovery.query(environment_id, collection_id, qopts)
    query['sent_msg'] = filter_str

    return jsonify(query)

@app.route('/compare/<int:file_id_1>/<int:file_id_2>')
def compare(file_id_1, file_id_2):
    with open('json_content/json_corpus_'+str(file_id_1)+'.json', 'r') as infile:
        json_content_1 = json.load(infile)
    with open('json_content/json_corpus_'+str(file_id_2)+'.json', 'r') as infile:
        json_content_2 = json.load(infile)

    return render_template('compare.html',v1=file_id_1,v2=file_id_2,content_json_1=json_content_1,content_json_2=json_content_2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)