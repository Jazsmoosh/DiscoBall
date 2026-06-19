from discoball.guess import guess_from_path, is_generic_rip_name


def test_generic_makemkv_uses_parent():
    g = guess_from_path('/watch/Half Baked (1998)/title_t00.mkv')
    assert g.query == 'Half Baked 1998'
    assert g.year == 1998


def test_generic_detector():
    assert is_generic_rip_name('title_t00')
    assert is_generic_rip_name('VTS_01_1')
    assert not is_generic_rip_name('The Matrix 1999')
