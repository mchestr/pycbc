import os
from functools import reduce

import boto3
import yaml
from copy import deepcopy
from cryptography.fernet import Fernet

from pycbc import json
from pycbc.utils import AttrDict as d

s3 = boto3.client('s3')
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
_DEFAULTS = d({
    'users': [],
    'encrypt_key': Fernet.generate_key().decode('utf-8'),
    'api_gateway': None,
    'sender_email': None,
    'logging': d({
        'version': 1,
        'formatters': d({
            'default': d({
                'format': '%(asctime)-15s - %(levelname)-7s - %(message)s',
            }),
        }),
        'handlers': d({
            'console': d({
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG',
                'stream': 'ext://sys.stderr',
            }),
        }),
        'loggers': d({
            'pycbc': d({
                'handlers': ['console'],
                'level': 'INFO',
            })
        })
    })
})


def load(event):
    event_override = event.get('config', d())
    env_prefix = event_override.get(
        'env_prefix', os.getenv('ENV_PREFIX', 'PYCBC_'))
    s3_bucket = event_override.get(
        's3_bucket', os.getenv(f'{env_prefix}S3_BUCKET', 'pycbc'))
    s3_filename = event_override.get(
        's3_filename',
        os.getenv(f'{env_prefix}S3_FILENAME', 'pycbc-config.yaml')
    )
    return json.loads(json.dumps(reduce(
        _merge,
        [
            deepcopy(_DEFAULTS),
            _from_s3(s3_bucket, s3_filename),
            _from_env(env_prefix),
            event_override,
        ])
    ))


def _merge(a, b, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge(a[key], b[key], path + [str(key)])
            else:
                a[key] = b[key]

        else:
            a[key] = b[key]
    return a


def _yaml_load(data):
    yaml.add_constructor(
        _mapping_tag,
        lambda loader, node: d(loader.construct_pairs(node)),
    )
    return yaml.load(data, Loader=yaml.FullLoader)


def _from_env(prefix):
    env_vars = (k for k in os.environ if k.startswith(prefix))
    return d({
        k[len(prefix):].lower(): os.environ[k] for k in env_vars
    })


def _from_s3(bucket, filename):
    fileobj = s3.get_object(
        Bucket=bucket,
        Key=filename,
    )
    return _yaml_load(fileobj['Body'].read())
