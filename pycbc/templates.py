import logging
import random

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


def generate_email(config, user, branches, encrypted_token, template='fancy_email.jinja2'):
    template = env.get_template(template)
    special_greeting = ''
    try:
        options = [jokes.generate(config), *user.get('special_greetings', [])]
        special_greeting = random.choice(options)
    except Exception as exc:
        log.exception(exc)

    content = template.render(branches=branches, token=encrypted_token,
                              api_gateway=config['api_gateway'],
                              name=user.first_name, special=special_greeting)
    return content
