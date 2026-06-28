from shipping import calc


def test_dw_0():
    assert calc(3, 1, 'express', True) == 18.0

def test_dw_1():
    assert calc(3, 1, 'express', False) == 20

def test_dw_2():
    assert calc(3, 1, 'standard', True) == 9.0

def test_dw_3():
    assert calc(3, 1, 'standard', False) == 10

def test_dw_4():
    assert calc(3, 2, 'express', True) == 28.8

def test_dw_5():
    assert calc(3, 2, 'express', False) == 32

def test_dw_6():
    assert calc(3, 2, 'standard', True) == 14.4

def test_dw_7():
    assert calc(3, 2, 'standard', False) == 16

def test_dw_8():
    assert calc(3, 3, 'express', True) == 43.2

def test_dw_9():
    assert calc(3, 3, 'express', False) == 48

def test_dw_10():
    assert calc(3, 3, 'standard', True) == 21.6

def test_dw_11():
    assert calc(3, 3, 'standard', False) == 24

def test_offdw_0():
    assert calc(1, 1, 'express', False) == 10

def test_offdw_1():
    assert calc(1, 1, 'standard', False) == 5

def test_offdw_2():
    assert calc(1, 3, 'express', False) == 24

def test_offdw_3():
    assert calc(1, 3, 'standard', False) == 12

def test_offdw_4():
    assert calc(5, 1, 'express', False) == 20

def test_offdw_5():
    assert calc(5, 1, 'standard', False) == 10

def test_offdw_6():
    assert calc(5, 3, 'express', False) == 48

def test_offdw_7():
    assert calc(5, 3, 'standard', False) == 24

def test_offdw_8():
    assert calc(0.5, 1, 'express', False) == 10

def test_offdw_9():
    assert calc(0.5, 1, 'standard', False) == 5

def test_offdw_10():
    assert calc(0.5, 3, 'express', False) == 24

def test_offdw_11():
    assert calc(0.5, 3, 'standard', False) == 12

def test_offdw_12():
    assert calc(100, 1, 'express', False) == 30

def test_offdw_13():
    assert calc(100, 1, 'standard', False) == 15

def test_offdw_14():
    assert calc(100, 3, 'express', False) == 72

def test_offdw_15():
    assert calc(100, 3, 'standard', False) == 36
