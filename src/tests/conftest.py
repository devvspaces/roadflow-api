from io import BytesIO
from typing import Callable, Dict, TypeVar
from unittest import TestCase

import pytest
from django.contrib.admin import AdminSite
from django.core.files.base import File
from model_bakery import baker
from PIL import Image
from rest_framework.test import APIClient
from utils.base.constants import User
from utils.base.general import get_tokens_for_user

U = TypeVar('U', bound=TestCase)

tcase = TestCase()


def assert_list_equal(a, b):
    """
    Assert that two lists are equal
    """
    if not isinstance(a, list):
        a = list(a)
    if not isinstance(b, list):
        b = list(b)
    tcase.assertListEqual(sorted(a), sorted(b))


basic_email = 'test_email@gmail.com'

drf_client = APIClient()

API_CLIENT_METHODS: Dict[str, Callable[..., None]] = {
    'post': drf_client.post,
    'patch': drf_client.patch,
    'put': drf_client.put,
    'delete': drf_client.delete,
    'get': drf_client.get,
}


class DummyStorage:
    """
    dummy message-store to test the api methods
    """

    def __init__(self):
        self.store = []

    def add(self, level, message, extra_tags=""):
        self.store.append(message)


@pytest.fixture
def user_manager():
    return User.objects


@pytest.fixture
def inactive_user():
    return baker.make(
        User,
        first_name='John', last_name='Doe'
    )


@pytest.fixture
def user_with_no_profile():
    return baker.make(
        User, active=True,
    )


@pytest.fixture
def user():
    user = baker.make(
        User, active=True,
    )
    user.set_password('test1234')
    user.save()
    return user


@pytest.fixture
def staff():
    return baker.make(
        User, active=True, staff=True,
    )


@pytest.fixture
def admin():
    return baker.make(
        User, active=True, staff=True,
        admin=True,
    )


@pytest.fixture
def message_storage():
    return DummyStorage()


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def request_storage(rf, message_storage):
    request = rf.get("/")
    request._messages = message_storage
    return request, message_storage


@pytest.fixture
def test_case():
    return TestCase()


@pytest.fixture
def base_client():

    def inner(method: str = "post"):
        client = API_CLIENT_METHODS[method]

        def child(url: str, data: dict = None, headers: dict = None):
            if headers is None:
                headers = {}

            return client(
                url, data, format='json',
                **headers
            )

        return child

    return inner


@pytest.fixture
def post(base_client):
    return base_client()


@pytest.fixture
def get(base_client):
    return base_client('get')


@pytest.fixture
def delete(base_client):
    return base_client('delete')


@pytest.fixture
def patch(base_client):
    return base_client('patch')


@pytest.fixture
def put(base_client):
    return base_client('put')


@pytest.fixture
def logged_client(base_client):

    def parent(method="post"):

        def inner(user, url, data=None, headers=None):
            if headers is None:
                headers = {}
            access_token = get_tokens_for_user(user)['access']
            headers['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            return base_client(method)(url, data, headers)

        return inner

    return parent


@pytest.fixture
def logged_post(logged_client):
    return logged_client()


@pytest.fixture
def logged_get(logged_client):
    return logged_client('get')


@pytest.fixture
def logged_delete(logged_client):
    return logged_client('delete')


@pytest.fixture
def logged_put(logged_client):
    return logged_client('put')


@pytest.fixture
def logged_patch(logged_client):
    return logged_client('patch')


@pytest.fixture
def dummy_request():
    class Request:
        user = None
    return Request()


@pytest.fixture(autouse=True)
def use_dummy_media_path(settings, tmp_path):
    settings.MEDIA_ROOT = settings.BASE_DIR / tmp_path


@pytest.fixture
def image_file(
    name='test.png', ext='png', size=(50, 50)
):
    file_obj = BytesIO()
    image = Image.new("RGB", size=size, color=(256, 0, 0))
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)
