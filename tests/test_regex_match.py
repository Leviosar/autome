from autome.regex.regex import Regex


def test_regex_match():
    """Test case for directly using the regex interface"""
    reg = Regex("(a|b)* (c|d)*")
    assert reg.match("abcd")
