"""Make some requests to OpenAI's chatbot"""

import time
import os 
import flask
import sys

from flask import g
from chatgpt_wrapper import OpenAIAPI

import wikipediaapi
import re
import urllib.parse
import wikipedia

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

bot = OpenAIAPI()
PORT = 5001 if '--port' not in sys.argv else int(sys.argv[sys.argv.index('--port') + 1])
APP = flask.Flask(__name__)

def summarize_text(text, language="english", num_sentences=10):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer = Stemmer(language)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)
    summary = summarizer(parser.document, num_sentences)
    return ' '.join([str(sentence) for sentence in summary])

def find_wikipedia_page_url(query):
    # Search Wikipedia for the query
    search_results = wikipedia.search(query)
    # Check if any results were found
    if not search_results:
        print(f"No Wikipedia page found for query: {query}")
        return None
    # Fetch the first search result
    page_title = search_results[0]
    page = wikipedia.page(page_title)
    # Return the URL of the page
    return page.url

def extract_url_and_page_title(input_string):
    # Regular expression to match URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    # Find the URL in the input string
    url_match = url_pattern.search(input_string)
    if url_match:
        url = url_match.group(0)
        # Parse the URL to extract the page title
        parsed_url = urllib.parse.urlparse(url)
        page_title = parsed_url.path.strip('/')
    else:
        url = None
        page_title = None
    return url, page_title

def extract_text_from_wikipedia(page_title, language='en'):
    # Create a Wikipedia API object for the specified language
    wiki_api = wikipediaapi.Wikipedia(language)
    # Fetch the Wikipedia page
    page = wiki_api.page(page_title)
    # Check if the page exists
    if not page.exists():
        print(f"The page '{page_title}' does not exist in '{language}' Wikipedia.")
        return None
    # Extract the text data and return it as a string
    text = page.text
    return text

phrase = "As of my last knowledge update in September 2021"

def get_wiki(query):
	page_url = find_wikipedia_page_url(query)
	url, page_title = extract_url_and_page_title(page_url)
	page_title
	page_title = page_title.split("/")[1]

	extract_text = extract_text_from_wikipedia(page_title)
	et = extract_text[0:3500]
	et

	message = "Can you answer this question " + query + "based  on this text " + et
	success, response, message = bot.ask(message)

	if success:
	    print("Response: ", response)

	else:
	    raise RuntimeError(message)

	return response

@APP.route("/chat", methods=["GET"])
def chat():
	message = flask.request.args.get("q")
	print("Sending message: ", message)
	success, response, message = bot.ask(message)
	if success:
		print("Response: ", response)
		if phrase in response:
		    response = get_wiki()
		    return response
		else:
			print("Response: ", response)
			return response
	else:
	    raise RuntimeError(message)

# @APP.route("/chat", methods=["GET"])
# def chat():
# 	query = flask.request.args.get("q")
# 	page_url = find_wikipedia_page_url(query)
# 	url, page_title = extract_url_and_page_title(page_url)
# 	page_title
# 	page_title = page_title.split("/")[1]

# 	extract_text = extract_text_from_wikipedia(page_title)
# 	et = extract_text[0:3500]
# 	et

# 	message = "Can you answer this question " + query + "based  on this text " + et
# 	success, response, message = bot.ask(message)

# 	if success:
# 	    print("Response: ", response)

# 	else:
# 	    raise RuntimeError(message)

# 	return response

def start_browser():
    APP.run(port=PORT, threaded=False)

if __name__ == "__main__":
    start_browser()

