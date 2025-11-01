import logging
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import exc
from sqlalchemy import inspect as sa_inspect
from collections.abc import Iterable

from .db import ScopedSession

logger = logging.getLogger(__name__)


class DatabaseServiceUnavailable(Exception):
    """Raised when the database is not available (OperationalError)."""


class BaseDAO:
    """Base DAO providing a session context helper.

    Use pattern:
        with self.new_session() as session:
            # use session

    DAOs will open/close their own sessions by default; callers should not
    pass sessions. This intentionally opts out of multi-call transactions.
    """

    @contextmanager
    def new_session(self) -> Iterator:
        session = ScopedSession()
        try:
            yield session
            session.commit()
        except exc.OperationalError:
            session.rollback()
            logger.exception('Database operational error')
            raise DatabaseServiceUnavailable()
        except BaseException:
            session.rollback()
            raise
        finally:
            ScopedSession.remove()

    def _use_session(self, func, *args, **kwargs):
        """Utility: always open a new session and run func(session, ...).

        Persistors are responsible for expunging returned ORM instances when
        a detached-but-readable result is desired.
        """
        with self.new_session() as s:
            return func(s, *args, **kwargs)



def expunge_result(session, result):
    """Detach `result` and its loaded related attributes from `session`.

    This function accepts a single ORM instance or an iterable of ORM
    instances. For each mapped instance it will attempt to access (and thus
    load) relationship attributes and recursively expunge those related
    instances/collections before expunging the instance itself. This keeps
    the related data available in-memory after the session is closed so it
    can be accessed later without lazy-loading from the DB.

    The implementation is best-effort and will silently ignore errors that
    occur while loading or expunging attributes to avoid blocking persistence
    operations.
    """
    if result is None:
        return

    visited = set()

    def _expunge(obj):
        # avoid re-visiting Python objects
        oid = id(obj)
        if oid in visited:
            return
        visited.add(oid)

        # If obj is a collection, iterate and expunge each item
        if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray)):
            for item in obj:
                try:
                    _expunge(item)
                except Exception:
                    # best-effort
                    pass
            return

        # Try to inspect as a mapped instance; if that fails, nothing to do
        try:
            inst = sa_inspect(obj)
        except Exception:
            # not a SQLAlchemy mapped instance
            return

        # Walk relationships and access them to ensure they're loaded, then
        # expunge related objects/collections recursively.
        try:
            mapper = inst.mapper
            for rel in mapper.relationships:
                try:
                    val = getattr(obj, rel.key)
                except Exception:
                    # accessing the attribute may fail; skip it
                    continue
                if val is None:
                    continue
                try:
                    _expunge(val)
                except Exception:
                    pass
        except Exception:
            # if any of the inspection steps fail, continue to expunge the
            # object itself
            pass

        # Finally expunge the instance from the session
        try:
            session.expunge(obj)
        except Exception:
            # ignore expunge failures
            pass

    # Top-level: handle iterables or single instance
    try:
        if isinstance(result, Iterable) and not isinstance(result, (str, bytes, bytearray)):
            for item in result:
                try:
                    _expunge(item)
                except Exception:
                    pass
        else:
            _expunge(result)
    except Exception:
        # swallow any unexpected errors - expunge is best-effort
        pass
