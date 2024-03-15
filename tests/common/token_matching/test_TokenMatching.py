from pygments.lexers import PythonLexer

from codelimit.common.lexer_utils import lex
from codelimit.common.token_matching.TokenMatching import match
from codelimit.common.token_matching.predicates.Lookahead import Lookahead
from codelimit.common.token_matching.predicates.Keyword import Keyword
from codelimit.common.token_matching.predicates.Name import Name


def test_match_keyword():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = match(tokens, Keyword("def"))

    assert len(result) == 2
    assert result[0].token_string() == "def"
    assert result[1].token_string() == "def"


def test_match_name():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = match(tokens, Name())

    assert len(result) == 2
    assert result[0].token_string() == "foo"
    assert result[1].token_string() == "bar"


def test_match_function_header():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = match(tokens, [Keyword("def"), Name()])

    assert len(result) == 2
    assert result[0].token_string() == "def foo"
    assert result[1].token_string() == "def bar"


def test_lookahead():
    code = "def foo(): pass\ndef bar(): pass\n"
    tokens = lex(PythonLexer(), code)

    result = match(tokens, [Keyword("def"), Lookahead(Name())])

    assert len(result) == 2
    assert result[0].token_string() == "def"
    assert result[1].token_string() == "def"
