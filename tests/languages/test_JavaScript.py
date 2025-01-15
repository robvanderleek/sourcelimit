from codelimit.languages import Languages
from tests.conftest import assert_units


def test_simple_function():
    code = """
    function foo() {
        return 'bar';
    }
    """

    assert_units(code, Languages.JavaScript, {"foo": 3})


def test_arrow_function():
    code = """
    const sayHello = async () => {
        console.log('Hello world!');
    }
    """

    assert_units(code, Languages.JavaScript, {"sayHello": 3})


def test_nested_functions():
    code = """
    function sayHelloWorld() {
        function sayHello() {
            console.log('Hello');
        }
        function sayWorld() {
            console.log('World');
        }
        sayHello();
        sayWorld();
    }

    sayHelloWorld();
    """

    assert_units(
        code,
        Languages.JavaScript,
        {"sayHelloWorld": 4, "sayHello": 3, "sayWorld": 3},
    )


def test_top_level_anonymous_functions_are_skipped():
    code = """
    function sayHelloWorld() {
        console.log('Hello World');
    }

    foo.on('sayHelloWorld', function () {
        console.log('Hello World');
    });
    """

    assert_units(code, Languages.JavaScript, {"sayHelloWorld": 3})

def test_nested_anonymous_functions_are_skipped():
    code = """
    const say = () => {
        function helloWorld() {
            console.log('Hello World');
        }

        foo.on('helloWorld', function () {
            console.log('Hello World');
        });
    }
    """

    assert_units(code, Languages.JavaScript, {"say": 5, "helloWorld": 3})


def test_skip_function_with_nocl_comment_in_header():
    code = """
    const bar = () => { // nocl
        console.log('Hello World from bar');
    }

    const foo = () => {
        console.log('Hello World from foo');
    }
    """

    assert_units(code, Languages.JavaScript, {"foo": 3})