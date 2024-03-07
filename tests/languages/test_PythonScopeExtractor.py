from pygments.lexers.python import PythonLexer

from codelimit.common.lexer_utils import lex
from codelimit.common.scope.scope_extractor_utils import build_scopes
from codelimit.languages.PythonScopeExtractor import (
    _get_indentation,
    PythonScopeExtractor,
    _get_token_lines,
)


def test_get_indentation():
    assert _get_indentation("foo = True") == 0
    assert _get_indentation(" foo = True") == 1
    assert _get_indentation("    foo = True") == 4
    assert _get_indentation("\tfoo = True") == 4
    assert _get_indentation("\t \t foo = True") == 10
    assert _get_indentation("") is None
    assert _get_indentation("  ") is None
    assert _get_indentation("\t") is None


def test_get_blocks_no_headers_no_blocks():
    code = ""

    tokens = lex(PythonLexer(), code)
    result = PythonScopeExtractor().extract_blocks(tokens, [])

    assert len(result) == 0


def test_get_blocks_single_header_single_block():
    code = ""
    code += "def foo():\n"
    code += "  foo = bar\n"

    tokens = lex(PythonLexer(), code)
    scope_extractor = PythonScopeExtractor()
    headers = scope_extractor.extract_headers(tokens)
    result = scope_extractor.extract_blocks(tokens, headers)

    assert len(result) == 1
    assert result[0].tokens[0].location.line == 2
    assert result[0].tokens[0].location.column == 3
    assert result[0].tokens[-1].location.line == 2
    assert result[0].tokens[-1].location.column == 9


def test_get_blocks_single_multiline_block():
    code = ""
    code += "def foo():\n"
    code += "  foo = bar\n"
    code += "  spam = eggs\n"

    tokens = lex(PythonLexer(), code)
    scope_extractor = PythonScopeExtractor()
    headers = scope_extractor.extract_headers(tokens)
    result = scope_extractor.extract_blocks(tokens, headers)

    assert len(result) == 1
    assert result[0].tokens[0].location.line == 2
    assert result[0].tokens[0].location.column == 3
    assert result[0].tokens[-1].location.line == 3
    assert result[0].tokens[-1].location.column == 10


def test_get_blocks_multi_blocks():
    code = ""
    code += "def foo():\n"
    code += "  pass\n"
    code += "\n"
    code += "def bar():\n"
    code += "  foo()\n"

    tokens = lex(PythonLexer(), code)
    scope_extractor = PythonScopeExtractor()
    headers = scope_extractor.extract_headers(tokens)
    result = scope_extractor.extract_blocks(tokens, headers)

    assert len(result) == 2

    print(result)

    assert result[0].tokens[0].location.line == 2
    assert result[0].tokens[-1].location.line == 2
    assert result[1].tokens[0].location.line == 5
    assert result[1].tokens[-1].location.line == 5


def test_trailing_global_code():
    code = ""
    code += "def foo():\n"
    code += "  pass\n"
    code += "\n"
    code += "bar = [\n"
    code += '  "bar"\n'
    code += "]\n"
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 2


def test_get_headers_no_headers():
    tokens = lex(PythonLexer(), "")
    result = PythonScopeExtractor().extract_headers(tokens)

    assert len(result) == 0


def test_get_headers_single_header():
    code = ""
    code += "def foo():\n"
    code += "  pass\n"
    tokens = lex(PythonLexer(), code)

    result = PythonScopeExtractor().extract_headers(tokens)

    assert len(result) == 1
    assert result[0].token_range[0].location.line == 1
    assert result[0].token_range[0].location.column == 1
    assert result[0].token_range[-1].location.line == 1
    assert result[0].token_range[-1].location.column == 9
    assert result[0].name == "foo"


def test_get_headers_multi_header():
    code = ""
    code += "def foo():\n"
    code += "  pass\n"
    code += "\n"
    code += "def bar():\n"
    code += "  foo()\n"
    tokens = lex(PythonLexer(), code)

    result = PythonScopeExtractor().extract_headers(tokens)

    assert len(result) == 2
    assert result[1].token_range[0].location.line == 4
    assert result[1].token_range[0].location.column == 1
    assert result[1].token_range[-1].location.line == 4
    assert result[1].token_range[-1].location.column == 9


def test_get_headers_multi_header_with_comment():
    code = ""
    code += "# def old_foo():\n"
    code += "def foo():\n"
    code += "  pass\n"
    code += "\n"
    code += "def bar():\n"
    code += "  foo()\n"
    tokens = lex(PythonLexer(), code)

    result = PythonScopeExtractor().extract_headers(tokens)

    assert len(result) == 2
    assert result[0].token_range[0].location.line == 2
    assert result[0].token_range[0].location.column == 1
    assert result[0].token_range[-1].location.line == 2
    assert result[0].token_range[-1].location.column == 9
    assert result[1].name == "bar"


def test_do_not_count_comment_lines():
    code = ""
    code += "def foo():\n"
    code += "# This is a comment\n"
    code += "  pass\n"
    code += "  # This is also a comment\n"
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 2


def test_header_with_defaults():
    code = ""
    code += "def foo(\n"
    code += "  bar: str = SomeClass(\n"
    code += "    'Hello'\n"
    code += "  ),\n"
    code += "  foo: str = SomeClass(\n"
    code += "    'World'\n"
    code += "  )\n"
    code += "):\n"
    code += "  pass\n"
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 9


def test_header_type_hints():
    code = ""
    code += "def foo(\n"
    code += "  bar: str\n"
    code += ") -> FooBar:\n"
    code += "  pass\n"
    tokens = lex(PythonLexer(), code)

    result = PythonScopeExtractor().extract_headers(tokens)

    assert len(result) == 1
    assert result[0].token_range.token_string() == "def foo ( bar : str )"


def test_two_functions():
    code = ""
    code += "def bar(\n"
    code += "    bar: Bar\n"
    code += ") -> JSONResponse:\n"
    code += "    bar = foo\n"
    code += "\n"
    code += "def foo(\n"
    code += "    foo: Foo\n"
    code += ") -> None:\n"
    code += "    foo = bar\n"
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 2
    assert len(result[0]) == 4
    assert len(result[1]) == 4


def test_skip_function_with_nocl_comment_in_header():
    code = ""
    code += "def bar(\n"
    code += "    bar: Bar\n"
    code += ") -> JSONResponse: # nocl\n"
    code += "    bar = foo\n"
    code += "\n"
    code += "def foo(\n"
    code += "    foo: Foo\n"
    code += ") -> None:\n"
    code += "    foo = bar\n"
    code += "    bar = foo\n"
    tokens = lex(PythonLexer(), code, False)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 5


def test_skip_function_with_nocl_comment_before_header():
    code = ""
    code += "def bar(\n"
    code += "    bar: Bar\n"
    code += ") -> JSONResponse:\n"
    code += "    bar = foo\n"
    code += "\n"
    code += "# NOCL\n"
    code += "def foo(\n"
    code += "    foo: Foo\n"
    code += ") -> None:\n"
    code += "    foo = bar\n"
    code += "    bar = foo\n"
    tokens = lex(PythonLexer(), code, False)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 4


def test_function_with_type_hints():
    code = ""
    code += "def foo(\n"
    code += "  bar: Bar\n"
    code += ") -> Foo:\n"
    code += "  bar = foo\n"
    code += "  foo = bar\n"
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 5


def test_line_continuation():
    code = ""
    code += "def say_hello():\n"
    code += "  print(\\\n"
    code += '"Hello " +\\\n'
    code += '"world")\n'
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 4


def test_if_statement():
    code = ""
    code += "def foo():\n"
    code += "  assert foo\n"
    code += "  if bar:\n"
    code += "    foo = bar\n"
    code += "  else:\n"
    code += "    bar = foo\n"
    tokens = lex(PythonLexer(), code)

    result = build_scopes(tokens, PythonScopeExtractor())

    assert len(result) == 1
    assert len(result[0]) == 6


def test_get_token_lines():
    code = ""
    code += "def foo():\n"
    code += "  pass\n"
    tokens = lex(PythonLexer(), code)

    result = _get_token_lines(tokens)

    assert len(result) == 2
    assert str(result[0]) == "[def, foo, (, ), :]"
    assert str(result[1]) == "[pass]"
