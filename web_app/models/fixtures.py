# coding:utf-8

import datetime
from sqlalchemy import event as sa_event
from ..core import db, FromCache, get_model, after_commit
from ..caching import regions
from ..helpers.sa_helper import JsonSerializableMixin, MutableList
from sqlalchemy.dialects.postgresql import JSON, ARRAY


class Fixture(db.Model, JsonSerializableMixin):
    __tablename__ = 'fixtures'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    intro = db.Column(db.UnicodeText(), nullable=False)
    profile = db.Column(JSON())
    attachment = db.Column(JSON)
    assets = db.Column(JSON())
    cover = db.Column(db.Unicode(256), nullable=False)
    size = db.Column(db.Unicode(64), nullable=True)
    year = db.Column(db.Unicode(20), nullable=True)
    origin_place = db.Column(db.Unicode(128), nullable=True)
    author = db.Column(db.Unicode(32), nullable=True)
    create_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    update_at = db.Column(db.DateTime(), nullable=True)
    # tag_ids = db.Column(MutableList.as_mutable(ARRAY(db.Integer)))
    # pattern_ids = db.Column(MutableList.as_mutable(ARRAY(db.Integer)))
    tag_ids = db.Column(ARRAY(db.Integer))
    pattern_ids = db.Column(ARRAY(db.Integer))

    @property
    def tags(self):
        tag_model = get_model('Tag')
        return [tag_model.from_cache_by_id(tag_id) for tag_id in self.tag_ids]

    @property
    def patterns(self):
        pattern_model = get_model('Pattern')
        return [pattern_model.from_cache_by_id(pattern_id) for pattern_id in self.pattern_ids]

    @property
    def download_times(self):
        return db.session.query(FixtureDownload).with_entities(FixtureDownload.number_of_times). \
            filter(FixtureDownload.fixture_id == self.id).scalar()

    def increase_download(self):
        FixtureDownload.query.filter(FixtureDownload.fixture_id == self.id). \
            update({FixtureDownload.number_of_times: FixtureDownload.number_of_times + 1}, synchronize_session=False)

    @classmethod
    def from_cache_by_id(cls, fixture_id):
        return Fixture.query.options(FromCache('model', 'fixture:%s' % fixture_id)). \
            filter(Fixture.id == fixture_id).first()

    def __eq__(self, other):
        if isinstance(other, Fixture) and other.name == self.name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<Fixture<id=%d>>' % self.id


class FixtureDownload(db.Model):
    __tablename__ = 'fixture_download'

    fixture_id = db.Column(db.Integer(), db.ForeignKey('fixtures.id', ondelete='cascade'), primary_key=True)
    number_of_times = db.Column(db.Integer(), default=0)

    def __eq__(self, other):
        if isinstance(other, FixtureDownload) and other.fixture_id == self.fixture_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.fixture_id)

    def __repr__(self):
        return '<FixtureDownload<fixture_id=%d>>' % self.fixture_id


@sa_event.listens_for(Fixture, 'after_insert')
@sa_event.listens_for(Fixture, 'after_update')
@sa_event.listens_for(Fixture, 'after_delete')
def on_fixture(mapper, connection, fixture):
    def do_after_commit():
        regions['model'].delete('fixture:%s' % fixture.id)

    after_commit(do_after_commit)
