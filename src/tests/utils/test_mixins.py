import pytest
from django.db import models
from utils.base.mixins import ModelChangeFunc


@pytest.mark.django_db
class TestModelChangeMixin:

    class _Model(ModelChangeFunc):
        field = models.CharField(max_length=100)
        other = models.CharField(max_length=100)
        check = None

        def check_field(self):
            self.check = True

        monitor_change = {
            'field': check_field,
        }

    class NoModelCheck(ModelChangeFunc):
        field = models.CharField(max_length=100)
        other = models.CharField(max_length=100)

    class SimilarModelCheck(ModelChangeFunc):
        field = models.CharField(max_length=100)
        other = models.CharField(max_length=100)
        check = None

        def check_field(self):
            self.check = True

        monitor_change = {
            'field': check_field,
            'other': check_field,
        }

    def test_monitor_change_fields(self):
        assert self._Model().monitor_change_fields == ['field']

    def test_monitor_change_fields_no_model_check(self):
        assert self.NoModelCheck().monitor_change_fields == []

    def test_monitor_change_funcs(self):
        assert self._Model().monitor_change_funcs == set([
            self._Model.check_field,
        ])

    def test_monitor_change_funcs_no_model_check(self):
        assert self.NoModelCheck().monitor_change_funcs == set()

    def test_monitor_change_funcs_similar_model_check(self):
        assert self.SimilarModelCheck().monitor_change_funcs == set([
            self.SimilarModelCheck.check_field,
        ])

    def test_get_clone_field(self):
        assert self._Model().get_clone_field('field') == '__field'

    def test_get_attr(self):
        model = self._Model(
            field='test1',
            other='test2',
        )
        model.save()
        assert model.get_attr('field') == 'test1'
        assert model.get_attr('other') == 'test2'

    def test_call_updates(self):
        model = self._Model(
            field='test1',
            other='test2',
        )
        model.save()
        assert model.check is None
        assert model.field == 'test1'

        model.call_updates()
        assert model.check is True
        assert model.field == 'test1'

    def test_model_change_func_valid_change(self):
        model = self._Model(
            field='test1',
            other='test2',
        )
        model.save()
        assert model.check is None
        assert model.field == 'test1'

        model.field = 'test'
        model.save()
        assert model.check is True
        assert model.field == 'test'

    def test_model_change_func_no_change(self):
        model = self._Model(
            field='test1',
            other='test2',
        )
        model.save()
        assert model.check is None
        assert model.field == 'test1'

        model.field = 'test1'
        model.save()
        assert model.check is None
        assert model.field == 'test1'

    def test_model_change_func_invalid_change(self):
        model = self._Model(
            field='test1',
            other='test2',
        )
        model.save()
        assert model.check is None
        assert model.field == 'test1'

        model.other = "error"
        model.save()
        assert model.check is None
        assert model.field == 'test1'
        assert model.other == 'error'
