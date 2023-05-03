"""Make some requests to OpenAI's chatbot"""

import time
import os 
import flask
import sys

from flask import g

from playwright.sync_api import sync_playwright

import requests, time

PROFILE_DIR = "/tmp/playwright" if '--profile' not in sys.argv else sys.argv[sys.argv.index('--profile') + 1]
PORT = 5001 if '--port' not in sys.argv else int(sys.argv[sys.argv.index('--port') + 1])
APP = flask.Flask(__name__)
PLAY = sync_playwright().start()
BROWSER = PLAY.firefox.launch_persistent_context(
    user_data_dir=PROFILE_DIR,
    headless=False,
)
PAGE = BROWSER.new_page()


def apiSearch(query: str, numResults: int, timePeriod: str='', region: str=''):

    searchParams = ''
    searchParams += f'q={query}'
    searchParams += f'&max_results={numResults}'
    if timePeriod:
        searchParams += f'&time={timePeriod}'
    if region:
        searchParams += f'&region={region}'

    url = f'https://ddg-webapp-aagd.vercel.app/search?{searchParams}'

    response = requests.get(url)

    results = response.json()

    return results

def prepare_results(results):
    i=1
    res = ""
    for result in results:
        res+=f'[{i}] "{result["body"]}"\nURL: {result["href"]}\n\n'
        i+=1
    return res

def headers(results):
    res = []
    for result in results:
        #res.append({'text':f'[{i}] {result["title"]}', 'link':result["href"]})
        res.append(result["href"])
    return res

def compile_prompt(prompt, results, reply_in = 'language of the query'):
    return f'''Web search results:

{prepare_results(results)}
Current date: {time.strftime("%d.%m.%Y")}

Instructions: Instructions: Using the provided web search results, write a comprehensive reply to the given query. Make to write answer in language of request. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.
Query: {prompt}'''

def Webify(query: str, numResults: int, timePeriod: str='', region: str='', reply_in: str='same languge as Query'):
    searchResults = apiSearch(query, numResults, timePeriod, region)
    return compile_prompt(query, searchResults, reply_in), headers(searchResults)

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
    while PAGE.query_selector(".result-streaming") is not None:
        time.sleep(.1)
    page_elements = PAGE.query_selector_all(".flex.flex-col.items-center > div")
    last_element = page_elements[-2]
    return last_element.inner_text()

@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    print("Sending message: ", message)
    message2 = Webify(message,7)
    #print(message2)
    send_message(message2[0])
    #time.sleep(10)
    response = get_last_message()
    print("Response: ", response)
    return response

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