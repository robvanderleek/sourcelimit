from codelimit.languages import LanguageName
from tests.common.ScopeExtractorTestCase import assert_units


def test_simple_function():
    code = """
    function foo() {
        return 'bar';
    }
    """

    assert_units(code, LanguageName.JavaScript, {"foo": 3})
