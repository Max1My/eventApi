from datetime import datetime, timedelta

import pytest
from loguru import logger
from starlette import status
from starlette.testclient import TestClient

from main import get_application
from src.core.domain.users.requests import AuthUser
from src.tests.configs import base_headers
from src.tests.test_users import create_user, create_admin, signin

app = get_application()

client = TestClient(app)

route = '/api/v1/events/'


@pytest.mark.asyncio
async def test_event_api():
    user_token = create_user()
    admin = await create_admin()
    admin_token = signin(AuthUser(
        username=admin.username,
        password='password'
    ))
    user_create_event(user_token)
    admin_create_event(admin_token)
    user_delete_event(user_token)
    admin_delete_event(admin_token)
    get_events()
    get_event()


def get_events():
    response = client.get(
        url=route,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text


def user_create_event(user_token):
    base_headers['Authorization'] = 'Bearer ' + user_token
    request = {
        'name': 'Интересное собрание',
        'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'finished_at': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    }
    response = client.post(
        url=route,
        headers=base_headers,
        json=request
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
    logger.error('Only admin can create event')


def admin_create_event(admin_token: str):
    base_headers['Authorization'] = 'Bearer ' + admin_token
    request = {
        'name': 'Интересное собрание',
        'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'finished_at': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    }
    response = client.post(
        url=route,
        headers=base_headers,
        json=request
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    logger.error('Event successfully created')


def get_event():
    response = client.get(
        url=f'{route}/1',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text


def user_delete_event(user_token: str):
    base_headers['Authorization'] = 'Bearer ' + user_token
    response = client.delete(
        url=f'{route}/1',
        headers=base_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
    logger.info('Ony admin can delete event')


def admin_delete_event(admin_token: str):
    base_headers['Authorization'] = 'Bearer ' + admin_token
    response = client.delete(
        url=f'{route}/1',
        headers=base_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
    logger.info('Event successfully deleted')
