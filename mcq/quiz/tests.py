from django.test import TestCase

from quiz.views import _render_choice_html, _render_stem_html


class StemRenderingTests(TestCase):
    def test_br_tags_become_rendered_line_breaks(self):
        html = str(_render_stem_html("Line 1<br>Line 2"))
        self.assertIn("Line 1<br>Line 2", html)

    def test_inline_html_is_preserved_for_trusted_stems(self):
        html = str(_render_stem_html("This is <em>important</em>."))
        self.assertIn("This is <em>important</em>.", html)

    def test_plain_text_stems_still_use_markdown_rendering(self):
        html = str(_render_stem_html("This is *important*."))
        self.assertIn("This is <em>important</em>.", html)

    def test_choice_html_preserves_latex_delimiters_for_mathjax(self):
        html = str(_render_choice_html("$PV = \\dfrac{PMT_t}{(1 + r)^t}$"))
        self.assertIn("$PV =", html)
        self.assertIn("\\dfrac{PMT_t}{(1 + r)^t}$", html)
        self.assertNotIn("<p>", html)
        self.assertIn("PMT_t", html)
