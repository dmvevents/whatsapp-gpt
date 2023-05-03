import requests, time

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

    Instructions: Using the provided web search results, write a comprehensive reply to the given query. Make sure to cite results using [number] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.
    Query: {prompt}
    Reply in {reply_in}'''

def Webify(query: str, numResults: int, timePeriod: str='', region: str='', reply_in: str='undefined'):
    searchResults = apiSearch(query, numResults, timePeriod, region)
    return compile_prompt(query, searchResults, reply_in), headers(searchResults)

if __name__ == '__main__':
    print(Webify('Testing', 3))