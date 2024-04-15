import os
from datetime import datetime

from sqlalchemyseed import load_entities_from_json
from sqlalchemyseed import Seeder
from dateutil.parser import parse

from src.core.domain import db_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def convert_date(data):
    for values in data['data']:
        try:
            values.update(
                (k, datetime.strptime(v, '%Y-%m-%d %H:%M:%S')) for k, v in values.items() if is_date(v))
        except ValueError:
            continue


async def insert_value():
    try:
        async with db_engine.session() as session:
            async with session.begin():
                seeder = Seeder(session)
                roles_entities = load_entities_from_json(os.path.join(BASE_DIR, 'roles.json'))
                users_entities = load_entities_from_json(os.path.join(BASE_DIR, 'users.json'))
                events_entities = load_entities_from_json(os.path.join(BASE_DIR, 'events.json'))
                convert_date(events_entities)
                seeder.seed(roles_entities)
                seeder.seed(users_entities)
                seeder.seed(events_entities)
                await seeder.session.commit()
    except Exception as e:
        print(f'error: {e}')
