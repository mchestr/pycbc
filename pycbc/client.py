import logging
import ssl

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

from pycbc import json
from pycbc.utils import AttrDict as d

log = logging.getLogger(__name__)


class TlsAdapter(HTTPAdapter):
    CIPHERS = (
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-ECDSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES256-SHA384',
        'ECDHE-ECDSA-AES256-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES128-SHA256',
        'AES256-SHA',
    )

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(
            ciphers=':'.join(self.CIPHERS),
            cert_reqs=ssl.CERT_REQUIRED,
            options=self.ssl_options
        )
        self.poolmanager = PoolManager(
            *pool_args,
            ssl_context=ctx,
            **pool_kwargs
        )


class WebBookingClient:
    BASE_URL = 'https://onlinebusiness.icbc.com'
    BASE_PATH = '/qmaticwebbooking/rest/schedule'

    SERVICES_URL = BASE_URL + BASE_PATH + '/services'
    CONFIGURATION_URL = BASE_URL + BASE_PATH + '/configuration'

    BRANCHES_URL = BASE_URL + BASE_PATH + '/branches'
    BRANCHES_AVAILABLE_URL = BRANCHES_URL + '/available'
    BRANCH_DATES_URL = BRANCHES_URL + '/{branch_id}/dates'
    BRANCH_DATES_TIMES_URL = BRANCH_DATES_URL + '/{date}/times'

    APPOINTMENTS_URL = BASE_URL + BASE_PATH + '/appointments'
    APPOINTMENTS_SEARCH_URL = APPOINTMENTS_URL + '/search'
    APPOINTMENT_URL = APPOINTMENTS_URL + '/{appointment_id}'
    APPOINTMENT_RESERVE_URL = BRANCH_DATES_TIMES_URL + '/{time}/reserve'
    APPOINTMENT_CHECK_MULTIPLE_URL = APPOINTMENTS_URL + '/checkMultiple'
    APPOINTMENT_CONFIRM_URL = APPOINTMENT_URL + '/confirm'

    DEFAULT_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) '
                  'Gecko/20100101 Firefox/81.0')

    def __init__(self, session=None):
        self._session = self._mount_adapter(session or requests.session())

    def configuration(self):
        return self._get(self.CONFIGURATION_URL)

    def services_search(self):
        return self._get(self.SERVICES_URL)

    def branches_service_search(self, service_id):
        return self._get(self.BRANCHES_AVAILABLE_URL, servicePublicId=service_id)

    def branches_dates_search(self, service_id, branch_id):
        url = self._format_url(self.BRANCH_DATES_URL, branch_id=branch_id)
        return self._get(url, servicePublicId=service_id, customSlotLength=15)

    def branches_times_search(self, service_id, branch_id, date):
        url = self._format_url(self.BRANCH_DATES_TIMES_URL, branch_id=branch_id, date=date)
        return self._get(url, servicePublicId=service_id, customSlotLength=15)

    def appointments_search(self, first_name, last_name, email, phone):
        data = {
            'captcha': False,
            'dob': '',
            'email': email,
            'externalId': '',
            'firstName': first_name,
            'lastName': last_name,
            'phone': phone
        }
        return self._post(self.APPOINTMENTS_SEARCH_URL, data)

    def appointment_cancel(self, appointment_id):
        url = self._format_url(self.APPOINTMENT_URL, appointment_id=appointment_id)
        return self._delete(url)

    def appointment_reserve(self, service_id, service_name, service_qp_id, branch_id, date, time):
        url = self._format_url(self.APPOINTMENT_RESERVE_URL, time=time, branch_id=branch_id, date=date)
        data = {
            'custom': json.dumps({
                'peopleServices': [{
                    'publicId': service_id,
                    'qpId': service_qp_id,
                    'adult': 1,
                    'name': service_name,
                    'child': 0,
                }]
            }),
            'services': [{
                'publicId': service_id,
            }],
        }
        return self._post(url, data, customSlotLength=15)

    def appointment_check_multiple(self, service_id, date, time, phone, email):
        return self._get(self.APPOINTMENT_CHECK_MULTIPLE_URL,
                         phone=phone, email=email, servicePublicId=service_id,
                         date=date, time=time)

    def appointment_confirm(self, service_id, service_name, service_qp_id, appointment_id,
                            first_name, last_name, email, phone, date_of_birth):
        url = self._format_url(self.APPOINTMENT_CONFIRM_URL,
                               appointment_id=appointment_id)
        data = {
            'captcha': '',
            'custom': json.dumps({
                'peopleServices': [{
                    'publicId': service_id,
                    'qpId': service_qp_id,
                    'adult': 1,
                    'name': service_name,
                    'child': 0,
                }],
                'totalCost': 0,
                'createdByUser': 'Qmatic Web Booking',
                'customSlotLength': 15,
            }),
            'customer': {
                'dateOfBirth': date_of_birth,
                'dob': '',
                'email': email,
                'externalId': '',
                'firstName': first_name,
                'lastName': last_name,
                'phone': phone,
            },
            'languageCode': 'en',
            'notes': '',
            'notificationType': '',
            'title': 'Qmatic Web Booking',
        }
        return self._post(url, data)

    def _mount_adapter(self, session):
        adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
        session.mount('https://', adapter)
        session.headers['User-Agent'] = self.DEFAULT_UA
        return session

    @staticmethod
    def _check_response(response):
        if response.status_code != 200:
            log.error(response.content)
            response.raise_for_status()

    @staticmethod
    def _format_url(url, **params):
        return url.format(**params)

    @staticmethod
    def _append_search_params(url, **query_params):
        query_params = ';'.join(f'{k}={v}' for k, v in query_params.items())
        if query_params:
            return f'{url};{query_params}'
        return url

    def _get(self, url, **query_params):
        url = self._append_search_params(url, **query_params)

        resp = self._session.get(url, timeout=5)
        self._check_response(resp)
        return resp.json(object_pairs_hook=d)

    def _post(self, url, data, **query_params):
        url = self._append_search_params(url, **query_params)
        resp = self._session.post(url, json=data, timeout=5)
        self._check_response(resp)
        return resp.json(object_pairs_hook=d)

    def _delete(self, url):
        resp = self._session.delete(url, timeout=5)
        self._check_response(resp)
