from backend.parser import parse

def test_two_houses():
    assert parse('Build two red houses')['actions'][0] == {'action': 'add', 'type': 'house', 'count': 2, 'color': 'red'}

def test_landmark_not_duplicated():
    a = parse('Place three trees beside the lake')['actions']
    assert len(a) == 1
    assert a[0]['type'] == 'tree' and a[0]['count'] == 3
    assert a[0]['relation'] == 'near' and a[0]['target'] == 'lake'

def test_multiple_entities():
    a = parse('Build a house and a castle')['actions']
    assert [o['type'] for o in a] == ['house', 'castle']

def test_removal():
    assert parse('Remove all the trees')['actions'][0]['action'] == 'remove'

def test_settings():
    a = parse('Make it night with rain')['actions']
    assert {'action':'setting', 'key':'time', 'value':'night'} in a
    assert {'action':'setting', 'key':'weather', 'value':'rain'} in a

def test_empty():
    try:
        parse('')
    except ValueError:
        pass
    else:
        raise AssertionError('Expected input validation')

def test_village_and_multi_relation():
    acts = parse('Put a lake behind the houses, a bridge across the river, and three trees beside the road')['actions']
    assert [(a['type'], a.get('relation'),a.get('target')) for a in acts] == [('lake','above','house'),('bridge','across','river'),('tree','near','road')]
    assert acts[-1]['count'] == 3
    assert parse('Build a small village')['actions'][0]['count'] == 4
