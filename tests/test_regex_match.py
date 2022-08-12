from autome.regex.regex import Regex


def test_regex_match():
    """Test case for directly using the regex interface"""
    
    # Simple regex
    reg = Regex("(a|b)* (c|d)*")
    assert reg.match("abcd")

    # Simple regex with string escaping (yes that's a really weird regex)
    reg = Regex(r"(\*|\()* (c|d)*")
    assert reg.match("*(cd")
