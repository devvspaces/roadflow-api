from utils.base import permissions
import pytest


class TestIsAuthenticatedAdmin:

    @property
    def perm(self):
        return permissions.IsAuthenticatedAdmin()

    @pytest.mark.parametrize(
        'is_authenticated, staff, admin, expected',
        [
            (True, True, False, True),
            (True, False, True, True),
            (True, False, False, False),
            (False, False, False, False),
        ]
    )
    def test_has_permission(
        self, mocker, is_authenticated, staff, admin, expected
    ):
        mock_request = mocker.Mock()
        mock_request.user = mocker.Mock()
        mock_request.user.is_authenticated = is_authenticated
        mock_request.user.staff = staff
        mock_request.user.admin = admin

        assert self.perm.has_permission(mock_request, None) is expected
