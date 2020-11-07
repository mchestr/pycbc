import pytest

from pycbc.handlers import search


@pytest.fixture
def mock_time_searches(branches_times_search_gen):
    branches_times_search_gen('2021-01-06')
    branches_times_search_gen('2021-01-07')
    branches_times_search_gen('2021-01-09')


@pytest.mark.freeze_time('2021-01-01')
def test_available_timeslots(service_search_stub, branches_service_search_stub,
                             branches_dates_search_stub, mock_time_searches,
                             date_search_output):
    output = search.available_timeslots(dict(
        service_ids=['27'],
        month_offset=1,
        max_times=3,
        branches=['Burnaby'],
        debug=False,
    ))
    assert output == [date_search_output]


@pytest.mark.freeze_time('2020-10-01')
def test_available_timeslots_no_dates(service_search_stub,
                                      branches_service_search_stub,
                                      branches_dates_search_stub):
    output = search.available_timeslots(dict(
        service_ids=['27'],
        month_offset=1,
        max_times=3,
        branches=['Burnaby'],
        debug=False,
    ))
    assert output == []
