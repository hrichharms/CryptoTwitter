import requests
import pandas as pd
import json
import ast
import yaml


def create_twitter_url():  # adjust query to skip retweets/media if needed, add fields/expansions
    handle = "elonmusk"
    max_results = 100
    mrf = "max_results={}".format(max_results)
    q = "query=from:{}".format(handle)
    url = "https://api.twitter.com/2/tweets/search/recent?{}&{}".format(
        mrf, q
    )
    return url


def main():
    url = create_twitter_url()
    data = process_yaml()
    bearer_token = create_bearer_token(data)
    res_json = twitter_auth_and_connect(bearer_token, url)
    documents = lang_data_shape(res_json)
    language_api_url, sentiment_url, subscription_key = connect_to_azure(data)
    headers = azure_header(subscription_key)
    with_languages = generate_languages(headers, language_api_url, documents)
    json_lines = combine_lang_data(documents, with_languages)
    document_format = add_document_format(json_lines)
    sentiments = sentiment_scores(headers, sentiment_url, document_format)
    score = sentiments["documents"][0]["score"]
    print(score)
    score_logic(score)


def process_yaml():
    with open("config.yaml") as file:
        return yaml.safe_load(file)


def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]


def twitter_auth_and_connect(bearer_token, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.request("GET", url, headers=headers)
    return response.json()


def lang_data_shape(res_json):
    data_only = res_json["data"]
    doc_start = '"documents": {}'.format(data_only)
    str_json = "{" + doc_start + "}"
    dump_doc = json.dumps(str_json)
    doc = json.loads(dump_doc)
    return ast.literal_eval(doc)


def connect_to_azure(data):
    azure_url = "https://cryptotwitter.cognitiveservices.azure.com/"
    language_api_url = "{}text/analytics/v2.1/languages".format(azure_url)
    sentiment_url = "{}text/analytics/v2.1/sentiment".format(azure_url)
    subscription_key = data["azure"]["subscription_key"]
    return language_api_url, sentiment_url, subscription_key


def generate_languages(headers, language_api_url, documents):
    response = requests.post(language_api_url, headers=headers, json=documents)
    return response.json()


def combine_lang_data(documents, with_languages):
    langs = pd.DataFrame(with_languages["documents"])
    lang_iso = [x.get("iso6391Name")
                for d in langs.detectedLanguages if d for x in d]
    data_only = documents["documents"]
    tweet_data = pd.DataFrame(data_only)
    tweet_data.insert(2, "language", lang_iso, True)
    json_lines = tweet_data.to_json(orient="records")
    return json_lines


def add_document_format(json_lines):
    docu_format = '"' + "documents" + '"'
    json_docu_format = "{}:{}".format(docu_format, json_lines)
    docu_align = "{" + json_docu_format + "}"
    jd_align = json.dumps(docu_align)
    jl_align = json.loads(jd_align)
    return ast.literal_eval(jl_align)


def sentiment_scores(headers, sentiment_url, document_format):
    response = requests.post(
        sentiment_url, headers=headers, json=document_format)
    return response.json()


def score_logic(score):
    if score >= 0.75:
        print("Positive")
    elif score >= 0.45:
        print("Neutral")
    else:
        print("Negative")


if __name__ == "__main__":
    main()
