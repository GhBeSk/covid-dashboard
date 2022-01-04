import sched
import time
import json
import requests
from flask import redirect
from flask.helpers import url_for

f = open("config.json")
data = json.load(f)


def news_API_request(covid_terms=data["news_keyword"]):
    f = open("config.json")
    data = json.load(f)
    r = requests.get(
        f"https://newsapi.org/v2/everything?q={covid_terms}&from=2021-12-14&sortBy=popularity&apiKey={data['api_key']}"
    )
    if r.status_code == 200:
        data = r.json()
        return data


def update_news(s, update_interval, update_name):
    try:
        s.enter(
            update_interval,
            2,
            redirect,
            argument=(url_for("index")),
            kwargs={"name": update_name},
        )
    except:
        s = sched.scheduler(time.time, time.sleep)
        s.enterabs(update_interval, 2, redirect, argument=(url_for("index")))
    s.run(blocking=False)
    return s
