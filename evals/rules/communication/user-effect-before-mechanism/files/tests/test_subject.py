import unittest

from digest.subject import render_subject


class RenderSubjectTest(unittest.TestCase):
    def test_render_subject_short(self):
        self.assertEqual(render_subject("This week in gardening"), "This week in gardening")

    def test_render_subject_limit(self):
        self.assertLessEqual(len(render_subject("word " * 30)), 60)

    def test_render_subject_width(self):
        title = "This week: spring planting, soil testing and the best tomatoes to grow"
        self.assertEqual(render_subject(title), "This week: spring planting, soil testing and the best...")
