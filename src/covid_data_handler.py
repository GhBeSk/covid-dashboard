import csv, sched
import time, json
from datetime import datetime, timedelta
from uk_covid19 import Cov19API

f = open("config.json", encoding="utf-8")
data = json.load(f)

s = sched.scheduler(time.time, time.sleep)


def parse_csv_data(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        result = []
        for row in reader:
            result.append(row)
    return result


def process_covid_csv_data(covid_csv_data):
    # current_date = datetime.strptime(
    #     "2021-10-28", "%Y-%m-%d"
    # )  # temporary placed with 28 oct
    current_date=datetime.now()     # will be placed when we have live data
    days = timedelta(7)
    min_date = current_date - days
    print(min_date)
    last_7_days_data = 0
    total_deaths = None
    current_hospital_cases = None
    for count, row in enumerate(covid_csv_data):
        if count > 0:
            if datetime.strptime(row[3], "%Y-%m-%d") >= min_date:
                if row[6]:
                    last_7_days_data += int(row[6])
            if total_deaths is None and row[4]:
                total_deaths = int(row[4])
            if current_hospital_cases is None and row[5]:
                current_hospital_cases = int(row[5])
    return (last_7_days_data, current_hospital_cases, total_deaths)


def covid_API_request(location=data["location"], location_type="ltla", **kwargs):
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate",
    }
    england_only = [f"areaType={location_type}", f"areaName={location}"]
    api = Cov19API(filters=england_only, structure=cases_and_deaths)
    data = api.get_json()
    # print(data)
    data = data["data"]
    datalist = []
    for i in data:
        datalist.append(
            [
                i["areaCode"],
                i["areaName"],
                location_type,
                i["date"],
                i["cumDeaths28DaysByDeathDate"],
                i["cumCasesByPublishDate"],
                i["newCasesByPublishDate"],
            ]
        )
    outfile = open("test.json", "w")
    outfile.write(str(data))
    outfile.close()
    prepend_to_csv(datalist)
    return data


def prepend_to_csv(data, file_name="nation_2021-10-28.csv"):
    previous_data = []
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        for row in reader:
            previous_data.append(row)
    all_data = previous_data[1:] + data
    # all_data=all_data[:10]
    l = len(all_data)
    quickSort(all_data, 0, l - 1)
    with open(file_name, "w", newline="") as outfile:
        csvwriter = csv.writer(outfile)
        csvwriter.writerow(previous_data.pop(0))
        csvwriter.writerows(all_data)
    print("updated_data")
    return True


def partition(arr, low, high):
    i = low - 1  # index of smaller element
    print(arr[high])
    pivot = datetime.strptime(arr[high][3], "%Y-%m-%d")  # pivot
    for j in range(low, high):
        if datetime.strptime(arr[j][3], "%Y-%m-%d") >= pivot:
            # increment index of smaller element
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quickSort(arr, low, high):
    if len(arr) == 1:
        return arr
    if low < high:
        par = partition(arr, low, high)
        quickSort(arr, low, par - 1)
        quickSort(arr, par + 1, high)


def schedule_covid_updates(update_interval, update_name):
    global s
    if update_interval != "dummy":
        executeschedule(update_interval, update_name)
    return s


def executeschedule(update_interval, update_name):
    s.enterabs(update_interval, 1, covid_API_request, kwargs={"name": update_name})
    s.run(blocking=False)


def get_schedule():
    global s
    return s


def get_csv_data_local():
    data = parse_csv_data("nation_2021-10-28.csv")
    filtered = []
    filtered_countries = []
    (
        last_7_days_new_cases_temp,
        current_hospital_cases,
        total_deaths,
    ) = process_covid_csv_data(data)
    for count, row in enumerate(data):
        if count > 0:
            if row[2] == "ltla":
                filtered.append(row)
            else:
                filtered_countries.append(row)
    # print("filtered_countries", filtered_countries)
    (
        last_7_days_new_cases,
        current_hospital_cases,
        total_deaths,
    ) = process_covid_csv_data(filtered)
    (
        last_7_days_new_cases_national,
        current_hospital_cases,
        total_deaths,
    ) = process_covid_csv_data(filtered_countries)
    return (
        filtered[0][1],
        last_7_days_new_cases,
        filtered_countries[0][1],
        last_7_days_new_cases_national,
        current_hospital_cases,
        total_deaths,
    )
