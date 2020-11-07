import logging

import arrow
import calendar
from jinja2 import Environment, PackageLoader, select_autoescape

from pycbc import jokes

log = logging.getLogger(__name__)
env = Environment(loader=PackageLoader('pycbc', 'templates'),
                  autoescape=select_autoescape())


def weekday(date):
    return calendar.day_name[arrow.get(date).weekday()]


env.globals['weekday'] = weekday


def generate_email(config, name, branches, encrypted_token, template='fancy_email.jinja2'):
    template = env.get_template(template)
    joke = ''
    try:
        joke = jokes.generate()
    except Exception as exc:
        log.exception(exc)

    content = template.render(branches=branches, token=encrypted_token,
                              api_gateway=config['api_gateway'],
                              name=name, joke=joke)
    return content
