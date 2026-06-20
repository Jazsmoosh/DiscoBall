from discoball.config import Config
from discoball.models import MediaMatch
from discoball.naming import build_destination


def test_discoball_naming():
    cfg = Config(output_dir='/out')
    m = MediaMatch(title='Half Baked', year=1998, primary_genre='Comedy', source='DVD')
    folder, file = build_destination(m, '/watch/title_t00.mkv', '/out', cfg)
    assert folder.endswith('/Half Baked (1998) [Comedy] {DVD}')
    assert file == 'Half Baked (1998) [Comedy] {DVD}.mkv'
