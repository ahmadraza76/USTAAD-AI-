import unittest
from ai import sanitize_input, is_hindi

class TestBot(unittest.TestCase):
    def test_sanitize_input(self):
        self.assertEqual(sanitize_input("Hello <script>alert('x')</script>"), "Hello alertx")
        self.assertEqual(len(sanitize_input("A" * 600)), 500)

    def test_is_hindi(self):
        self.assertTrue(is_hindi("हेलो"))
        self.assertFalse(is_hindi("Hello"))

if __name__ == '__main__':
    unittest.main()
