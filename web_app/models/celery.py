# coding:utf-8

from sqlalchemy.dialects.postgresql import JSON
import datetime
from ..core import db
from ..helpers.sa_helper import JsonSerializableMixin


class CeleryTaskLog(db.Model, JsonSerializableMixin):
    __tablename__ = "celery_task_log"

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    args = db.Column(JSON, nullable=True)
    kwargs = db.Column(JSON, nullable=True)
    retries = db.Column(db.Integer(), default=0)
    retval = db.Column(db.Unicode(256), nullable=True)
    exception = db.Column(db.Unicode(512), nullable=True)
    status = db.Column(db.SmallInteger(), nullable=True, default=0)  # -2:retry, -1:failure, 1:success,
    create_at = db.Column(db.DateTime(), default=datetime.datetime.now)
