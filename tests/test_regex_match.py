from autome.regex.regex import Regex

def test_regex_match():
    reg = Regex('(a|b)* (c|d)*')
    assert reg.match('abcd')