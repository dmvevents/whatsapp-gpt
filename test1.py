import requests
import json

def get_answer(question, api_key, search_engine_id, num_results=1):
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={question}&num={num_results}"
    response = requests.get(url)
    data = json.loads(response.text)

    if "items" not in data:
        print("No results found.")
        return None

    result = data["items"][0]
    title = result["title"]
    link = result["link"]
    snippet = result["snippet"]

    return {
        "title": title,
        "link": link,
        "snippet": snippet
    }

def main():
    # Replace with your API key and custom search engine ID
    api_key = "AIzaSyDeB_IiWqx01Xjr8k0IJHOwbo8Ps1Fysxk"
    search_engine_id = "95cf8ffaadcd14c22"

    question = input("Please enter your question: ")
    answer = get_answer(question, api_key, search_engine_id)

    if answer:
        print("\nTitle:", answer["title"])
        print("Link:", answer["link"])
        print("Snippet:", answer["snippet"])

if __name__ == "__main__":
    main()