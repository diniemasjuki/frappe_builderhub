from __future__ import annotations

from types import SimpleNamespace

from frappe.tests import UnitTestCase

from builder_hub.plugins.responses import set_plugin_icon_cache_headers

ICON_PATH = "/files/plugin-icons/" + ("a" * 64) + ".svg"


def _response(status_code: int):
	return SimpleNamespace(status_code=status_code, headers={})


class IconCacheHeaderTests(UnitTestCase):
	def test_headers_are_set_only_on_a_served_icon(self):
		response = _response(200)
		set_plugin_icon_cache_headers(response, SimpleNamespace(path=ICON_PATH))
		self.assertEqual(response.headers["Content-Type"], "image/svg+xml")
		self.assertIn("immutable", response.headers["Cache-Control"])

	def test_other_paths_are_untouched(self):
		response = _response(200)
		set_plugin_icon_cache_headers(response, SimpleNamespace(path="/app/hub-plugin"))
		self.assertEqual(response.headers, {})
