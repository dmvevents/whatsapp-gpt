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

bot = OpenAIAPI()
PORT = 5001 if '--port' not in sys.argv else int(sys.argv[sys.argv.index('--port') + 1])
APP = flask.Flask(__name__)


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

    print(page_title)
    print(page.url)
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
        page_title = parsed_url.path.strip('/').replace('_', ' ')
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



@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    # new_m = "what is the last know wikipedia url to answer this question: " + message + " . I just need the url nothing else."
    
    # print("Sending message: ", new_m)
    # #send_message(message)
    # #response = get_last_message()
    # #print("Response: ", response)

    # success, response, message = bot.ask(message)

    # page_title = ""
    page_url = find_wikipedia_page_url(message)
    url, page_title = extract_url_and_page_title(page_url)

    text = extract_text_from_wikipedia(page_title)

    m2 = "Answer " + message + " based on this info " + text
    success, response, message = bot.ask(m2)

    if success:
        print("Response: ", response)

    else:
        raise RuntimeError(message)

    return response

def start_browser():
    APP.run(port=PORT, threaded=False)

if __name__ == "__main__":
    start_browser()