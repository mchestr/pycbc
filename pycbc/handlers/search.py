import logging
import logging.config
from typing import List, TypedDict

import arrow

from pycbc import client
from pycbc.aws import sns
from pycbc.config import load
from pycbc.utils import AttrDict as d

log = logging.getLogger(__name__)


class Input(TypedDict):
    service_ids: List[str]
    month_offset: int
    max_times: int
    branches: List[str]
    debug: bool


def handler(event, context):
    config = load(event)
    logging.config.dictConfig(config.logging)

    data = available_timeslots(event)
    if data and config.get('sns_topic'):
        for service in data:
            sns.publish(config.sns_topic, service)
    else:
        log.info('No SNS topic configured')
    return data


def available_timeslots(input_data: Input):
    input_data = _set_defaults(input_data)
    log.info(f'Input: {input_data}')
    pycbc = client.WebBookingClient()

    services = filter(
        lambda s: (not input_data.service_ids or s.qpId in input_data.service_ids),
        pycbc.services_search()
    )

    results = []
    for service in services:
        log.info(f'Searching for branches for {service}')
        branches_for_service = pycbc.branches_service_search(service.publicId)

        output = d(service, branches={})
        branches_to_select = set(input_data.branches)
        before_date = arrow.now().shift(months=input_data.month_offset)
        for branch in filter(lambda b: b.name in branches_to_select, branches_for_service):
            log.info(f'Searching for dates for branch {branch}')
            branch_dates = pycbc.branches_dates_search(service.publicId, branch.id)
            available_dates = (data.date for data in branch_dates if arrow.get(data.date) <= before_date)

            available_datetimes = d()
            for _, date in zip(range(input_data.max_times), available_dates):
                available_datetimes[date] = [
                    t.time for t in pycbc.branches_times_search(
                        service.publicId, branch.id, date)
                ]

            if not available_datetimes:
                continue

            output.branches[branch['name']] = d(branch, available_dates=available_datetimes)
        if output.branches:
            results.append(output)

    return results


def _set_defaults(input_data):
    return d(
        service_ids=input_data.get('service_ids', []),
        month_offset=input_data.get('month_offset', 1),
        max_times=input_data.get('max_times', 3),
        branches=input_data.get('branches', []),
        debug=input_data.get('debug', False)
    )
