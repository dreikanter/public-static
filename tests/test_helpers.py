# encoding: utf-8

from publicstatic import helpers


def test_md():
    title = 'This is a title'
    test_data = """
        title: Page title
        created: 2010/08/13
        tasg: #hello

        # {title}

        """.format(title=title)
    assert helpers.get_h1(test_data) == title


def main():
    test_md()


if __name__ == '__main__':
    main()

