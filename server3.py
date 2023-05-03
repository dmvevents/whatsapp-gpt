"""Make some requests to OpenAI's chatbot"""

import time
import os 
import flask
import sys

from flask import g

from playwright.sync_api import sync_playwright

import wikipediaapi
import re
import urllib.parse
import wikipedia

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

PROFILE_DIR = "/tmp/playwright" if '--profile' not in sys.argv else sys.argv[sys.argv.index('--profile') + 1]
PORT = 5001 if '--port' not in sys.argv else int(sys.argv[sys.argv.index('--port') + 1])
APP = flask.Flask(__name__)
PLAY = sync_playwright().start()
BROWSER = PLAY.firefox.launch_persistent_context(
    user_data_dir=PROFILE_DIR,
    headless=False,
)
PAGE = BROWSER.new_page()
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

phrase = "September 2021"

def get_wiki(query):
    page_url = find_wikipedia_page_url(query)
    url, page_title = extract_url_and_page_title(page_url)
    page_title
    page_title = page_title.split("/")[1]

    extract_text = extract_text_from_wikipedia(page_title)
    et = extract_text[0:3500]
    et

    message = "Can you answer this question " + query + "based  on this text " + et
    send_message(message)
    response = get_last_message()
    return response

def get_input_box():
    """Find the input box by searching for the largest visible one."""
    textareas = PAGE.query_selector_all("textarea")
    candidate = None
    for textarea in textareas:
        if textarea.is_visible():
            if candidate is None:
                candidate = textarea
            elif textarea.bounding_box().width > candidate.bounding_box().width:
                candidate = textarea
    return candidate

def is_logged_in():
    try:
        return get_input_box() is not None
    except AttributeError:
        return False

def send_message(message):
    # Send the message
    box = get_input_box()
    box.click()
    box.fill(message)
    box.press("Enter")
    while PAGE.query_selector(".result-streaming") is not None:
        time.sleep(1.1)

def get_last_message():
    """Get the latest message"""
    page_elements = PAGE.query_selector_all(".flex.flex-col.items-center > div")
    print(page_elements)
    last_element = page_elements[-2]
    return last_element.inner_text()

@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    print("Sending message: ", message)
    send_message(message)
    response = get_last_message()
    if phrase in response:
            response = get_wiki(message)
            return response
    else:
        print("Response: ", response)
        return response
    # print("Response: ", response)
    # return response

def start_browser():
    PAGE.goto("https://chat.openai.com/")
    APP.run(port=PORT, threaded=False)
    if not is_logged_in():
        print("Please log in to OpenAI Chat")
        print("Press enter when you're done")
        input()
    else:
        print("Logged in")
        
if __name__ == "__main__":
    start_browser()