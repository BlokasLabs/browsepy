
import re
import unittest
import warnings

import browsepy.transform
import browsepy.transform.glob


class TestStateMachine(unittest.TestCase):
    module = browsepy.transform

    def test_nearest_error(self):
        m = self.module.StateMachine()
        self.assertRaises(KeyError, lambda: m.nearest)


class TestGlob(unittest.TestCase):
    module = browsepy.transform.glob
    translate = staticmethod(module.translate)

    def assertSubclass(self, cls, base):
        self.assertIn(base, cls.mro())

    def test_glob(self):
        translations = [
            ('/a', r'^/a(/|$)'),
            ('a', r'/a(/|$)'),
            ('/a*', r'^/a[^/]*(/|$)'),
            ('/a**', r'^/a.*(/|$)'),
            ('a?', r'/a[^/](/|$)'),
            ('/a{b,c}', r'^/a(b|c)(/|$)'),
            ('/a[a,b]', r'^/a[a,b](/|$)'),
            ('/a[!b]', r'^/a[^b](/|$)'),
            ('/a[!/]', r'^/a[^/](/|$)'),
            ('/a[]]', r'^/a[\]](/|$)'),
            ('/a\0', r'^/a\u0000(/|$)'),
            ('/a\\*', r'^/a\*(/|$)'),
            ('a{,.{txt,py[!od]}}', r'/a(|\.(txt|py[^od]))(/|$)'),
            ('a,a', r'/a,a(/|$)'),
            ]
        self.assertListEqual(
            [self.translate(g, sep='/') for g, r in translations],
            [r for g, r in translations]
            )

        translations = [
            ('/a', r'^\\a(\\|$)'),
            ('a', r'\\a(\\|$)'),
            ('/a*', r'^\\a[^\\]*(\\|$)'),
            ('/a**', r'^\\a.*(\\|$)'),
            ('a?', r'\\a[^\\](\\|$)'),
            ('/a{b,c}', r'^\\a(b|c)(\\|$)'),
            ('/a[a,b]', r'^\\a[a,b](\\|$)'),
            ('/a[!b]', r'^\\a[^b](\\|$)'),
            ('/a[!/]', r'^\\a[^\\](\\|$)'),
            ('/a[]]', r'^\\a[\]](\\|$)'),
            ('/a\\*', r'^\\a\*(\\|$)'),
            ]
        self.assertListEqual(
            [self.translate(g, sep='\\') for g, r in translations],
            [r for g, r in translations]
            )

    def test_unicode(self):
        tests = [
            ('/[[:alpha:][:digit:]]', (
                '/a',
                '/ñ',
                '/1',
                '/à',
                ), (
                '/_',
                )),
            ('/[[:alpha:]0-5]', (
                '/a',
                '/á',
                ), (
                '/6',
                '/_',
                )),
            ]
        for pattern, matching, nonmatching in tests:
            pattern = re.compile(self.translate(pattern, sep='/'))
            for test in matching:
                self.assertTrue(pattern.match(test))
            for test in nonmatching:
                self.assertFalse(pattern.match(test))

    def test_unsupported(self):
        translations = [
            ('[[.a-acute.]]a', '/.a(/|$)'),
            ('/[[=a=]]a', '^/.a(/|$)'),
            ('/[[=a=]\\d]a', '^/.a(/|$)'),
            ('[[:non-existent-class:]]a', '/.a(/|$)'),
            ]
        for source, result in translations:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.assertEqual(self.translate(source, sep='/'), result)
                self.assertSubclass(w[-1].category, Warning)
