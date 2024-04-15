import pytest
from loguru import logger
from starlette import status
from starlette.testclient import TestClient

from src.core.domain.roles.dto import RoleEnum
from src.core.domain.users.requests import RegisterUser, AuthUser
from main import get_application
from src.core.domain.users.service import UserService
from src.tests.configs import base_headers

app = get_application()

client = TestClient(app)

route = '/api/v1/user'


@pytest.mark.asyncio
async def test_users_api():
    user_token = create_user()
    create_admin_by_user(user_token)
    await create_admin_by_admin()
    signin_bad_credentials()


@pytest.mark.asyncio
def create_user():
    request = RegisterUser(
        first_name='Егор',
        username='egor_113443',
        password='password'
    )
    response = client.post(
        url=f'{route}/register',
        headers={"Content-Type": "application/json"},
        json=request.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    logger.info('User created successfully')
    return response.json()['access_token']


@pytest.mark.asyncio
def create_admin_by_user(user_token):
    request = RegisterUser(
        first_name='Елена',
        username='elena_922',
        password='password'
    )
    base_headers['Authorization'] = 'Bearer ' + user_token
    logger.info(f'headers: {base_headers}')
    response = client.post(
        url=f'{route}/register/admin',
        headers=base_headers,
        json=request.model_dump()
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
    logger.info('Only admin can register admin')


@pytest.mark.asyncio
async def create_admin_by_admin():
    admin = await create_admin()
    user_token = signin(AuthUser(
        username=admin.username,
        password='password'
    ))
    base_headers['Authorization'] = 'Bearer ' + user_token
    request = RegisterUser(
        first_name='Елена',
        username='elena_65',
        password='password'
    )
    response = client.post(
        url=f'{route}/register/admin',
        headers=base_headers,
        json=request.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    logger.info('Admin registered successfully')


@pytest.mark.asyncio
def signin_bad_credentials():
    request = AuthUser(
        username='oleg',
        password='passwOrt'
    )
    response = client.post(
        url=f'{route}/signin',
        headers={"Content-Type": "application/json"},
        json=request.model_dump()
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    logger.error('Bad credentials')


@pytest.mark.asyncio
def signin(request: AuthUser | None = None):
    if request is None:
        request = AuthUser(
            username='oleg',
            password='password'
        )
    response = client.post(
        url=f'{route}/signin',
        headers={"Content-Type": "application/json"},
        json=request.model_dump()
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    logger.info('Signin successful')
    return response.json().get('access_token')


@pytest.mark.asyncio
async def create_admin():
    request = RegisterUser(
        first_name='Дмитрий',
        username='dima_4166554',
        password='password'
    )
    return await UserService().register(request=request, role_name=RoleEnum.ADMIN.name)
