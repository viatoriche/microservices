from unittest import TestCase


class TestSmartDict(TestCase):
    def test_smart_dict(self):
        from microservices.helpers import SmartDict

        d = SmartDict(a='tested')
        self.assertEqual(d.a, 'tested')
        self.assertEqual(d['a'], 'tested')
        d.b = 'tested_b'
        self.assertEqual(d['b'], 'tested_b')
        self.assertEqual(d.b, 'tested_b')
        d.a = 'tested_a'
        self.assertEqual(d['a'], 'tested_a')
        d['c'] = 'tested_c'
        self.assertEqual(d.c, 'tested_c')
        del d.c
        self.assertEqual(d.c, None)
        self.assertEqual('c' not in d, True)
        del d['a']
        self.assertEqual(d.a, None)
        self.assertEqual('a' not in d, True)
