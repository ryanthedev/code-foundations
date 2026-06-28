from statement import statement

PLAYS={'hamlet': {'name': 'Hamlet', 'type': 'tragedy'}, 'as-like': {'name': 'As You Like It', 'type': 'comedy'}, 'othello': {'name': 'Othello', 'type': 'tragedy'}}


def test_dw_0_canonical():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'hamlet', 'audience': 55}, {'playID': 'as-like', 'audience': 35}, {'playID': 'othello', 'audience': 40}]}
    expected='Statement for BigCo\n Hamlet: $650.00 (55 seats)\n As You Like It: $580.00 (35 seats)\n Othello: $500.00 (40 seats)\nAmount owed is $1,730.00\nYou earned 47 credits\n'
    assert statement(invoice, PLAYS) == expected

def test_offdw_0_small_no_bonus():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'hamlet', 'audience': 10}, {'playID': 'as-like', 'audience': 5}]}
    expected='Statement for BigCo\n Hamlet: $400.00 (10 seats)\n As You Like It: $315.00 (5 seats)\nAmount owed is $715.00\nYou earned 1 credits\n'
    assert statement(invoice, PLAYS) == expected

def test_offdw_1_tragedy_boundary30():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'hamlet', 'audience': 30}]}
    expected='Statement for BigCo\n Hamlet: $400.00 (30 seats)\nAmount owed is $400.00\nYou earned 0 credits\n'
    assert statement(invoice, PLAYS) == expected

def test_offdw_2_comedy_boundary20():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'as-like', 'audience': 20}]}
    expected='Statement for BigCo\n As You Like It: $360.00 (20 seats)\nAmount owed is $360.00\nYou earned 4 credits\n'
    assert statement(invoice, PLAYS) == expected

def test_offdw_3_all_comedy():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'as-like', 'audience': 50}, {'playID': 'as-like', 'audience': 8}]}
    expected='Statement for BigCo\n As You Like It: $700.00 (50 seats)\n As You Like It: $324.00 (8 seats)\nAmount owed is $1,024.00\nYou earned 31 credits\n'
    assert statement(invoice, PLAYS) == expected

def test_offdw_4_single_tragedy_big():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'othello', 'audience': 100}]}
    expected='Statement for BigCo\n Othello: $1,100.00 (100 seats)\nAmount owed is $1,100.00\nYou earned 70 credits\n'
    assert statement(invoice, PLAYS) == expected

def test_offdw_5_zero_audience():
    invoice={'customer': 'BigCo', 'performances': [{'playID': 'hamlet', 'audience': 0}, {'playID': 'as-like', 'audience': 0}]}
    expected='Statement for BigCo\n Hamlet: $400.00 (0 seats)\n As You Like It: $300.00 (0 seats)\nAmount owed is $700.00\nYou earned 0 credits\n'
    assert statement(invoice, PLAYS) == expected
