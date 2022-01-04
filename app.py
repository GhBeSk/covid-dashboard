from datetime import datetime
import json
from logging.config import dictConfig
from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from src.covid_data_handler import (
    get_csv_data_local,
    get_schedule,
    schedule_covid_updates,
)
from src.covid_news_handling import news_API_request, update_news

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


app = Flask(__name__)
f = open("config.json", encoding="utf-8")
data = json.load(f)
app.config["SECRET_KEY"] = data["secret_key"]


global DELETED_NEWS
DELETED_NEWS = []


@app.route("/")
def index():
    """
    Returns the index page with all the initial data required
    """
    (
        local_location,
        last_7_days_cases,
        national_location,
        last_7_days_cases_national,
        current_hospital_cases,
        total_deaths,
    ) = get_csv_data_local()
    s_list = []
    try:
        schedule = get_schedule()
        s = schedule.queue
        print(s)
        for i in s:
            if "covid_API_request" in i[2].__name__:
                timestamp = datetime.fromtimestamp(i[0])
                time_mark = timestamp.strftime("%H:%M")
                content = f"Update for covid cases at {time_mark}"
            else:
                timestamp = datetime.fromtimestamp(i[0])
                time_mark = timestamp.strftime("%H:%M")
                content = f"Update for covid news at at {time_mark}"
            s_list.append({"title": i[4]["name"], "content": content})
    except Exception as e:
        app.logger.info(f"Error occured while getting scheduled updates {e}")
        print(e)
        pass
    news = news_API_request("Covid COVID-19 coronavirus")
    print(f"delete news {DELETED_NEWS}")
    news_updated = []
    for i in news["articles"]:
        if i["title"] not in DELETED_NEWS:
            news_updated.append(i)
    return render_template(
        "index.html",
        updates=s_list,
        news_articles=news_updated,
        local_7day_infections=last_7_days_cases,
        location=local_location,
        nation_location=national_location,
        national_7day_infections=last_7_days_cases_national,
        hospital_cases=current_hospital_cases,
        deaths_total=total_deaths,
    )


@app.route("/index", methods=["GET", "POST"])
def time_handler():
    """
    Handles all the updates posted to the backend on covid data and news.
    """
    if request.method == "POST":
        update = request.form.get("update")
        now = datetime.now()
        time_interval = now.replace(
            hour=int(update.split(":")[0]), minute=int(update.split(":")[1])
        ).timestamp()
        print(f"requst data {request.form.get('covid-data')}")
        if request.form.get("covid-data"):
            s_ = schedule_covid_updates(time_interval, request.form.get("two"))
            app.logger.info(f"Covid data update at {str(datetime.now().timestamp())}")
        else:
            s_ = schedule_covid_updates("dummy", request.form.get("two"))
        if request.form.get("news"):
            try:
                s_
            except:
                s_ = None
            update_news(s_, time_interval, request.form.get("two"))
            app.logger.info(f"Updating Covid news at {datetime.now().timestamp()}")
    return redirect(url_for("index"))


@app.route("/delete")
def delete_news():
    news_title = request.args.get("news-title")
    DELETED_NEWS.append(news_title)
    print(DELETED_NEWS)
    app.logger.info(f"User deleted news with title {news_title}")
    return redirect(url_for("index"))
