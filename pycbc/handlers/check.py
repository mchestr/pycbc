import logging
import logging.config

from pycbc import client, token
from pycbc.config import load

log = logging.getLogger(__name__)

_AVAILABLE = b'iVBORw0KGgoAAAANSUhEUgAAAAwAAAAQCAYAAAAiYZ4HAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAOhJREFUKJHNkMFNw0AURN//u6QJo0Qy9BFbpA0HEeoKSJgyjPYAbRAUQ5og6/0ckCM7yiUXxJzfSG8G/l0EYFsur1wna5mkZdbU7RDY3tzlrmMtPt5mTd0qgDP3jOrc9hp2i2o6hCUSgKL79g8AHiCZVioxIJrbnrBbVGU07yUSVJhiaeMmaXVQAmjn99cqMYBeGvZhJq6H5SKVvaoMdEclgGMYQM996VA4Vkrw+btpfISegtV3hTmKUyUFUEn1EM6aup29PG5MuhLSF6J5f6v2txrpzYmOBs7C03snVhi8uklcnbv3j/IDk1qBhz0yl7oAAAAASUVORK5CYII='
_UNAVAILABLE = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAbhJREFUOI2Nkz1oU2EUhp9z0lsT0duiGBDUUkQJVTDGSesPZLHioHHJXIcUETE1k7uDIDSDYNuMzoaCizg01IAQEGltB7fa2Um7JCU353MI19xUG/JOH+ec532/Hz5hnzLVhYwhcw7NojYBoOiOc67mxC19y81vROclXFx5v3y402m+FuThftOonFklHlixkS81/xp04dZHgeuD4FDmqCfawUwjX2oqQDd5OBhAhZstL1YGkEx1IeM09nU4UDDnejvBLqshc8PAY6Nx3t7Kc/vU+Z4hUlCHZoeBF6dzTI0nSR872WuYZDV8KoDUeJJnF2+gIv/AqbETvPuxxauteuRMTI5Ek55MXeNq8gxHvFFebNQ46h3qg19urvXdAcCIojvAOYDnXz6wOJ3j/sQFPI1x1j8+EDZsW51ztbCw297j0ecVvv/6yd3TqYEwgCCr6sQtRYtRk0EwgCgVAUhXy8uiWog2EzGPPQsOhHG8WX/w9LECxAMrmqMe7Tc77YNhY83/7ZcAFKCRLzUT7WDGmVX+T/Qn+7v+nU+zsy2I/MZQl1bKaUUKmGRRJruBti3IqiiV9XvFzej8H4xUvW+Yvt46AAAAAElFTkSuQmCC'


def handler(event, context):
    config = load(event)
    logging.config.dictConfig(config.logging)

    return {
        'statusCode': 200,
        'body': _generate_icon(config, event),
        'headers': {
            'Content-Type': 'image/png'
        },
        'isBase64Encoded': True,
    }


def _check_timeslot_available(service_id, branch_id, date, time):
    pycbc = client.WebBookingClient()
    available_times = pycbc.branches_times_search(service_id, branch_id, date)
    return any(time in t.time for t in available_times)


def _generate_icon(config, event):
    try:
        query_params = event['queryStringParameters']
        query_token = query_params.pop('token')

        payload = token.decrypt(config.encrypt_key, query_token, ttl=60 * 60 * 4)
    except Exception as exc:
        log.exception(exc)
        return _UNAVAILABLE
    log.info(f'Payload: {payload}')

    if _check_timeslot_available(payload.service.publicId, query_params['branch_id'],
                                 query_params['date'], query_params['time']):
        return _AVAILABLE
    return _UNAVAILABLE
