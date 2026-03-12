from django.test import TestCase

from quiz.views import _render_stem_html


class StemRenderingTests(TestCase):
    def test_br_tags_become_rendered_line_breaks(self):
        html = str(_render_stem_html("Line 1<br>Line 2"))
        self.assertIn("Line 1<br>Line 2", html)

    def test_other_html_is_escaped(self):
        html = str(_render_stem_html("Safe<script>alert(1)</script>"))
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
