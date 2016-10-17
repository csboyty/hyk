# coding:utf-8

import datetime
from ..core import BaseService, after_commit, db
from ..models import Fixture, FixtureDownload, Pattern


class FixtureService(BaseService):
    __model__ = Fixture

    def create_fixture(self, **kwargs):
        fixture = Fixture(name=kwargs.get('name'), intro=kwargs.get('intro'), profile=kwargs.get('profile'),
                          attachment=kwargs.get('attachment'),cover=kwargs.get('cover'), size=kwargs.get('size'),
                          year=kwargs.get('year'), origin_place=kwargs.get('origin_place'), author=kwargs.get('author'))

        fixture.tag_ids = list(set([int(tag_id) for tag_id in kwargs.get('tags', [])]))
        fixture.pattern_ids = list(
            set([int(asset_dict['pattern_id']) for asset_dict in kwargs.get('assets', []) if asset_dict['pattern_id']]))
        self.save(fixture)
        assets = []
        for asset_dict in kwargs.get('assets'):
            asset_dict['fixture_id'] = fixture.id
            assets.append(asset_dict)

        added, updated, deleted = _get_added_updated_deleted(updated_assets=assets)
        _update_patterns(fixture.id, added=added)
        db.session.add(FixtureDownload(fixture_id=fixture.id, number_of_times=0))

        def do_after_commit():
            update_fixture = db.session.query(Fixture).get(fixture.id)
            update_fixture.assets = list(assets)
            db.session.commit()

        after_commit(do_after_commit)
        return fixture

    def update_fixture(self, fixture_id, **kwargs):
        fixture = self.get_or_404(fixture_id)
        update_assets = []
        for asset_dict in kwargs.get('assets'):
            asset_dict['fixture_id'] = fixture_id
            update_assets.append(asset_dict)

        added, updated, deleted = _get_added_updated_deleted(fixture.assets, update_assets)

        fixture.name = kwargs.get('name')
        fixture.intro = kwargs.get('intro')
        fixture.profile = kwargs.get('profile')
        fixture.attachment = kwargs.get('attachment')
        fixture.assets = update_assets
        fixture.cover = kwargs.get('cover')
        fixture.size = kwargs.get('size')
        fixture.year = kwargs.get('year')
        fixture.origin_place = kwargs.get('origin_place')
        fixture.author = kwargs.get('author')
        fixture.tag_ids = list(set([int(tag_id) for tag_id in kwargs.get('tags', [])]))
        fixture.pattern_ids = list(
            set([int(asset_dict['pattern_id']) for asset_dict in kwargs.get('assets', []) if asset_dict['pattern_id']]))
        fixture.update_at = datetime.datetime.utcnow()
        self.save(fixture)
        _update_patterns(fixture_id, added=added, updated=updated, deleted=deleted)
        return fixture

    def delete_fixture(self, fixture_id):
        fixture = self.get_or_404(fixture_id)
        self.delete(fixture)
        _update_patterns(fixture_id, deleted=fixture.assets)

    def paginate_fixture(self, offset=0, limit=10, **kwargs):
        filters = []
        orders = [Fixture.create_at.desc()]
        query = db.session.query(Fixture, FixtureDownload.number_of_times).join(FixtureDownload,
                                                                                FixtureDownload.fixture_id == Fixture.id)
        if 'name' in kwargs and kwargs['name']:
            filters.append(Fixture.name.contains(kwargs['name']))
        if 'tag_ids' in kwargs and kwargs['tag_ids']:
            filters.append(Fixture.tag_ids.contains(map(int, kwargs['tag_ids'])))
        if 'pattern_ids' in kwargs and kwargs['pattern_ids']:
            filters.append(Fixture.pattern_ids.contains(map(int, kwargs['pattern_ids'])))
        if 'sort' in kwargs and kwargs['sort'] == 'downloads':
            orders.append(FixtureDownload.number_of_times.desc())

        data = []
        count = query.with_entities(db.func.count(Fixture.id)).filter(*filters).scalar()
        if count:
            if offset is None and limit is None:
                data = query.filter(*filters).order_by(*orders).all()
            else:
                data = query.filter(*filters).order_by(*orders).offset(offset).limit(limit).all()

        return count, data


fixture_service = FixtureService()

import itertools


def _get_added_updated_deleted(assets=[], updated_assets=[]):
    added = []
    updated = []
    deleted = []

    for update_asset_dict in updated_assets:
        orig_asset_dict = None
        for asset_dict in assets:
            if asset_dict['media_id'] == update_asset_dict['media_id']:
                orig_asset_dict = asset_dict
                assets.remove(asset_dict)
                break

        if not orig_asset_dict:
            if update_asset_dict['pattern_id']:
                added.append(update_asset_dict)
        elif orig_asset_dict != update_asset_dict:
            if orig_asset_dict['pattern_id'] == update_asset_dict['pattern_id']:
                if orig_asset_dict['pattern_id']:
                    updated.append(update_asset_dict)
            else:
                if orig_asset_dict['pattern_id'] and not update_asset_dict['pattern_id']:
                    deleted.append(orig_asset_dict)
                elif not orig_asset_dict['pattern_id'] and update_asset_dict['pattern_id']:
                    added.append(update_asset_dict)
                else:
                    deleted.append(orig_asset_dict)
                    added.append(update_asset_dict)

    deleted.extend(assets)
    return added, updated, deleted


def _update_patterns(fixture_id, added=[], updated=[], deleted=[]):
    pattern_ids = list(set(map(lambda asset_dict: asset_dict['pattern_id'], itertools.chain(added, updated, deleted))))
    patterns = Pattern.query.filter(Pattern.id.in_(pattern_ids)).all()
    pattern_assets = dict([(str(pattern.id), list(pattern.assets) if pattern.assets else []) for pattern in patterns])
    for new_asset_dict in added:
        if new_asset_dict['pattern_id']:
            p_assets = pattern_assets.get(new_asset_dict['pattern_id'])
            new_asset_dict['fixture_id'] = fixture_id
            p_assets.append(new_asset_dict)

    for update_asset_dict in updated:
        if update_asset_dict['pattern_id']:
            p_assets = pattern_assets.get(update_asset_dict['pattern_id'])
            try:
                asset_dict = next(asset_dict for asset_dict in p_assets if
                                  asset_dict['media_id'] == update_asset_dict['media_id'])
                asset_dict.update(update_asset_dict)
            except StopIteration:
                pass

    for delete_asset_dict in deleted:
        if delete_asset_dict['pattern_id']:
            p_assets = pattern_assets.get(delete_asset_dict['pattern_id'])
            p_assets.remove(delete_asset_dict)

    for pattern in patterns:
        pattern.assets = pattern_assets.get(str(pattern.id))
        db.session.add(pattern)
