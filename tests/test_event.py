import logging
from datetime import date
from unittest.mock import create_autospec, Mock

from arango_orm.event import dispatch, listen, listens_for

from .fixtures import test_db, ensure_person_collection, Person  # noqa: F401

log = logging.getLogger(__name__)


class BasePerson(object):
    pass


class MyPerson(BasePerson):
    def __init__(self, name):
        self.name = name

    def sleep(self):
        dispatch(self, "gone_sleep")


def _gone_sleep_notification(target, event, *args, **kwargs):
    log.debug("{0} has got in sleep~".format(target.name))


def test_event_works():
    mock_listener = create_autospec(_gone_sleep_notification)

    listen(MyPerson, "gone_sleep", _gone_sleep_notification)
    listen(MyPerson, "gone_sleep", mock_listener)

    p = MyPerson("Wonder")
    p.sleep()

    mock_listener.assert_called_once_with(p, "gone_sleep")


def test_listen_by_base_class():
    mock = Mock()

    listen(BasePerson, "gone_sleep", mock)

    p = MyPerson("James")
    p.sleep()

    mock.assert_called_once()  # only available in python 3.6 for builtin unittest.mock


def test_listens_for_decorator():
    mock = Mock()

    @listens_for(MyPerson, "gone_sleep")
    def gone_sleep_handler(*args, **kwargs):
        mock(*args, **kwargs)

    p = MyPerson("Wonder")
    p.sleep()
    mock.assert_called_once()  # only available in python 3.6 for builtin unittest.mock


def test_orm_events(test_db, ensure_person_collection):  # noqa: F811
    ma, mu, md = Mock(), Mock(), Mock()

    listen(Person, "post_add", ma)
    listen(Person, "post_update", mu)
    listen(Person, "post_delete", md)

    p = Person(name="Wonder", _key="10000", dob=date(year=2016, month=9, day=12))

    res = test_db.add(p)
    ma.assert_called_once_with(p, "post_add", db=test_db, result=res)

    res = test_db.update(p)
    mu.assert_called_once_with(p, "post_update", db=test_db, result=res)
    res = test_db.update(p)
    assert mu.call_count == 2

    res = test_db.delete(p)
    md.assert_called_once_with(p, "post_delete", db=test_db, result=res)
