from covid_data_handler import get_csv_data_local, parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates


def test_parse_csv_data():
    data = parse_csv_data("nation_2021-10-28.csv")

    assert len(data) == 639


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data("nation_2021-10-28.csv")
    )
    # assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)


def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name="update test")


def test_data_sorted():
    data = parse_csv_data("nation_2021-10-28.csv")
    flag = 0
    i = 1
    while i < len(data):
        if data[i][3] > data[i - 1][3]:
            flag = 1
        i += 1
    assert flag == 1


def test_local_data():
    (
        area_name,
        last_7_days_cases_local,
        country,
        last_7_days_cases_international,
        current_hospital_cases,
        total_deaths,
    ) = get_csv_data_local()
    assert area_name == "Exeter"
    assert last_7_days_cases_local == 5339
    assert country == "England"
    assert last_7_days_cases_international == 206057
    assert current_hospital_cases == 6951
    assert total_deaths == 141544
