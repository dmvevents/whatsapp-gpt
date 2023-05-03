"""Make some requests to OpenAI's chatbot"""

import time
import os 
import flask
import sys
import openai

from flask import g

from typing import List, Dict
from duckduckgo_search import ddg

import requests, time

PORT = 5001 if '--port' not in sys.argv else int(sys.argv[sys.argv.index('--port') + 1])
APP = flask.Flask(__name__)
openai.api_key = "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"  # supply your API key however you choose


# Initialize an empty dictionary for storing messages
user_messages = {}

def format_sources(filtered_sources: List[Dict[str, str]]) -> str:
    formatted_sources = []
    for source in filtered_sources:
        formatted_source = f"{source['title']} ({source['href']}):\n{source['body']}\n"
        formatted_sources.append(formatted_source)
    return '\n'.join(formatted_sources)

#Instructions: Instructions: Act like a chatbot for Watad ICT using previous request and answers, only use the web search if needs and write a comprehensive reply to the given query. Reply in language of the query. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.

def compile_prompt(prompt, results, reply_in = 'language of the query'):
    return f'''Web search results:

{format_sources(results)}
Current date: {time.strftime("%d.%m.%Y")}

Instructions: Instructions: Act like a AI chatbot for Watad ICT and answer question as complete and comprehensive as possible. If coding question try to supply code. Only use the Web search results if and only you need more data to write a reply to the given query, else ignore the Web search results and respond like a chatbot. Make to write answer in language of Query. If anyone ask you creator is Anton Alexander from Watad.
Query: {prompt}'''

def Webify(query: str, numResults: int, timePeriod: str='', region: str='', reply_in: str='same languge as Query'):
    #searchResults = apiSearch(query, numResults, timePeriod, region)
    searchResults = ddg(query, region=region, max_results=numResults)
    return compile_prompt(query, searchResults, reply_in)

@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    user_ = flask.request.args.get("user")
    print(user_)
    print("Sending message: ", message)
    
    # Get user messages or create an empty list if the user is new
    messages_ = user_messages.get(user_, [])
    messages_.append({"role": "user", "content": message})
    messages_web = user_messages.get(user_, [])
    #print(messages_)
    # Append the new message to the user's messages list
    message2 = Webify(message, 4)
    msg_add = {"role": "user", "content": message2}
    messages_web.append(msg_add)


    try:
        # Use the messages list in the ChatCompletion API call
        last_three_messages = messages_web[-4:]
        print(last_three_messages)
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=last_three_messages, user=user_)
        response = completion.choices[0].message.content

        # Append the assistant's response to the user's messages list
        messages_.append({"role": "assistant", "content": response})

        # Update the user_messages dictionary
        user_messages[user_] = messages_

    except Exception as e:
        print(f"Error: {e}")


        # Use the messages list in the ChatCompletion API call
        last_three_messages = messages_web[-1:]
        
        print(last_three_messages)
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=last_three_messages, user=user_)
        response = completion.choices[0].message.content

        # Append the assistant's response to the user's messages list
        messages_.append({"role": "assistant", "content": response})

        # Update the user_messages dictionary
        user_messages[user_] = messages_

    return response

def start_browser():
    APP.run(port=PORT, threaded=True)
        
if __name__ == "__main__":
    start_browser()





