# coding:utf-8

from flask import Blueprint, request, render_template, json
from ...models import Pattern, Fixture
from ...helpers.flask_helper import json_response

bp = Blueprint('user_patterns', __name__, url_prefix='/patterns')


@bp.route('/<int:pattern_id>', methods=['GET'])
def fixture_page(pattern_id):
    pattern = Pattern.from_cache_by_id(pattern_id)
    related_fixtures = Fixture.query.filter(Fixture.pattern_ids.any(pattern_id)).order_by(Fixture.create_at.desc()).limit(5).all()
    return render_template('frontend/patternDetail.html', pattern=pattern, related_fixtures=related_fixtures)


@bp.route('/<int:pattern_id>/download', methods=['GET'])
def download_pattern(pattern_id):
    pattern = Pattern.from_cache_by_id(pattern_id)
    pattern.increase_download()
    return render_template('frontend/patternDownload.html', download_url=pattern.attachment.get('url'))


@bp.route('/mget', methods=['GET'])
def get_patterns():
    pattern_ids = json.loads(request.args.get('ids'))
    patterns = []
    for pattern_id in pattern_ids:
        patterns.append(Pattern.from_cache_by_id(pattern_id))
    return json_response(patterns=patterns)
