# coding:utf-8

from flask import Blueprint, request, render_template
from ...models import Fixture
from ...helpers.flask_helper import json_response

bp = Blueprint('user_fixtures', __name__, url_prefix='/fixtures')


@bp.route('/<int:fixture_id>', methods=['GET'])
def fixture_page(fixture_id):
    fixture = Fixture.from_cache_by_id(fixture_id)
    related_fixtures = Fixture.query.filter(Fixture.tag_ids.contains(fixture.tag_ids), Fixture.id != fixture_id). \
        order_by(Fixture.create_at.desc()).limit(5).all()
    return render_template('frontend/single.html', fixture=fixture, related_fixtures=related_fixtures)


@bp.route('/<int:fixture_id>/download', methods=['GET'])
def download_fixture(fixture_id):
    fixture = Fixture.from_cache_by_id(fixture_id)
    fixture.increase_download()
    return render_template('frontend/fixtureDownload.html', download_url=fixture.attachment.get('url'))


@bp.route('/<int:fixture_id>/detail', methods=['GET'])
def get_fixture(fixture_id):
    fixture = Fixture.from_cache_by_id(fixture_id)
    return json_response(fixture=fixture)
