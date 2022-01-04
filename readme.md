# Covid Information Application #
Link to github : https://github.com/GhBeSk/covid-dashboard.git
## Project Setup ##

First, you will have to obtain the needed packages:
```
pip install -r requirements.txt
```
Then setup the application with making the driver file known, which will be done by:
```
set FLASK_APP=app.py
```
Then to run the server
```
flask run
```

This app has two functions as main views:

1. Index View
2. Update Data view (which redirects to index after execution)

We are using two modules:

1. Covid data handler
2. Covid News handler

### Covid Data Handler ###

Covid Data handler's function handle all the functions which are related the to the covid cases data, to update and read data from the api and the csv file.

#### parse_csv_data ####

Parse csv data uses python's csv module to read the data and get it into a nested list format.

#### Process_covid_csv_data ####

This function calls parse_csv data within itself and gives three parameters as response

* last 7 days deaths
* current hospital cases
* Total deaths

#### covid_api_request ####

Covid API request use the COVID19 API to request data from Public Health England api, and updates the csv file we maintain, in a descending order, we sort the data using a quicksort algorithm.

#### schedule_covid_update ####

This function schedules updates on when to request data from the api, at a given time.


### COVID News Handler ###

#### News_API_request ####

this function creates a request on [NewsAPI] (https://www.newsapi.org “NEWSAPI”) to fetch news regarding covid from the keywords defined. and display it on interface.

#### update_news ####

This function allows to schedule updates on caling news from the news_api_request on a given time interval.