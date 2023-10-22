from unittest import TestCase, main
from parser import Parser


class TestParser(TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse(self):
        self.assertEqual(self.parser.parse('group', '34', '6'), None)

    def test_quit(self):
        self.assertEqual(self.parser.quit(), None)


if __name__ == '__main__':
    main()
