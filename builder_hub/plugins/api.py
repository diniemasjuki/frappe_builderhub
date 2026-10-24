"""Public JSON API and authenticated actions for Builder Hub plugins."""

from __future__ import annotations

import json
from datetime import UTC

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import get_datetime, get_url
from frappe.utils.caching import redis_cache

from builder_hub.plugins import publishing, submission
from builder_hub.plugins.protocol import (
	CATALOG_PAGE_SIZE,
	PLUGIN_NAME_PATTERN,
	PLUGINS_API_VERSION,
	SCHEMA_VERSION,
	SEMVER_PATTERN,
	semver_key,
)


@frappe.whitelist(allow_guest=True)
def get_info() -> dict:
	return {
		"schema_version": SCHEMA_VERSION,
		"name": "Builder Hub",
		"plugins_api_version": PLUGINS_API_VERSION,
	}


@frappe.whitelist(allow_guest=True)
def get_catalog(protocol_version: int | str = 1, page: int | str = 1) -> dict:
	page = _page(page)
	items = _get_catalog(_protocol_version(protocol_version), get_url())
	start = (page - 1) * CATALOG_PAGE_SIZE
	return {
		"schema_version": SCHEMA_VERSION,
		"plugins": items[start : start + CATALOG_PAGE_SIZE],
		"page": page,
		"total_count": len(items),
		"has_more": start + CATALOG_PAGE_SIZE < len(items),
	}


@redis_cache(ttl=600)
def _get_catalog(protocol_version: int, base_url: str) -> list[dict]:
	"""One cached list for every page, so a page request does not build the catalog again."""
	items = []
	for plugin in frappe.get_all(
		"Hub Plugin",
		filters={"status": ("in", ["Published", "Deprecated"])},
		fields=_plugin_fields(),
		order_by="plugin_name asc",
		ignore_permissions=True,
	):
		publisher = _publisher(plugin.publisher)
		if not publisher or publisher.status != "Active":
			continue
		release = _latest_release(plugin.name, protocol_version)
		if release:
			items.append(_catalog_item(plugin, publisher, release, base_url))
	return items


@frappe.whitelist(allow_guest=True)
def get_plugin(name: str, protocol_version: int | str = 1) -> dict:
	protocol_version = _protocol_version(protocol_version)
	plugin = _public_plugin(name)
	publisher = _publisher(plugin.publisher)
	if not publisher or publisher.status != "Active":
		_not_found()
	releases = frappe.get_all(
		"Hub Plugin Release",
		filters={
			"plugin": plugin.name,
			"status": "Published",
			"protocol_version": ("<=", protocol_version),
		},
		fields=[
			"version",
			"protocol_version",
			"package_size",
			"package_sha256",
			"release_notes",
			"status",
			"published_on",
		],
		ignore_permissions=True,
	)
	releases.sort(key=lambda row: semver_key(row.version), reverse=True)
	latest = releases[0] if releases else None
	detail = _catalog_item(plugin, publisher, latest, get_url(), include_latest=False)
	detail["readme"] = plugin.readme or ""
	return {
		"schema_version": SCHEMA_VERSION,
		"plugin": detail,
		"releases": [
			{
				"version": row.version,
				"protocol_version": row.protocol_version,
				"package_size": row.package_size,
				"package_sha256": row.package_sha256,
				"release_notes": row.release_notes or "",
				"status": row.status,
				"published_on": _iso(row.published_on),
			}
			for row in releases
		],
	}


@frappe.whitelist(allow_guest=True)
def get_plugin_release(plugin_name: str, version: str) -> dict:
	_validate_identity(plugin_name, version)
	plugin = _public_plugin(plugin_name)
	publisher = _publisher(plugin.publisher)
	if not publisher or publisher.status != "Active":
		_not_found()
	name = f"{plugin_name}@{version}"
	if not frappe.db.exists("Hub Plugin Release", name):
		_not_found()
	release = frappe.get_doc("Hub Plugin Release", name)
	if release.status != "Published":
		frappe.throw(_("This release is not available for installation."), frappe.PermissionError)
	return {
		"schema_version": SCHEMA_VERSION,
		"release": {
			"plugin_name": release.plugin,
			"version": release.version,
			"protocol_version": release.protocol_version,
			"manifest": _json(release.manifest, {}),
			"github_release_url": release.github_release_url,
			"package_url": release.package_url,
			"package_size": release.package_size,
			"package_sha256": release.package_sha256,
			"status": release.status,
			"published_on": _iso(release.published_on),
		},
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def get_release_status(releases: list[dict] | str) -> dict:
	releases = _json(releases, None)
	if not isinstance(releases, list):
		frappe.throw(_("releases must be a JSON list."))
	if len(releases) > 100:
		frappe.throw(_("At most 100 release identities can be checked at once."))
	results = []
	for identity in releases:
		if not isinstance(identity, dict):
			frappe.throw(_("Each release identity must be an object."))
		plugin_name = identity.get("plugin_name")
		version = identity.get("version")
		_validate_identity(plugin_name, version)
		plugin = frappe.db.get_value(
			"Hub Plugin",
			plugin_name,
			["name", "publisher", "status", "replacement"],
			as_dict=True,
		)
		release = frappe.db.get_value(
			"Hub Plugin Release",
			f"{plugin_name}@{version}",
			["status"],
			as_dict=True,
		)
		found = bool(plugin and release)
		plugin_status = plugin.status if plugin else None
		if plugin:
			publisher_status = frappe.db.get_value("Hub Publisher", plugin.publisher, "status")
			if publisher_status == "Blocked":
				plugin_status = "Blocked"
		results.append(
			{
				"plugin_name": plugin_name,
				"version": version,
				"found": found,
				"plugin_status": plugin_status,
				"release_status": release.status if release else None,
				"replacement": plugin.replacement if plugin else None,
			}
		)
	return {"schema_version": SCHEMA_VERSION, "releases": results}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60, methods="POST")
def request_publication(
	repository_url: str,
	categories: list[str] | str | None = None,
) -> dict:
	return submission.request_publication(repository_url, categories)


@frappe.whitelist()
def approve_publication_request(request_name: str, reason: str | None = None) -> dict:
	return submission.approve_publication_request(request_name, reason)


@frappe.whitelist()
def reject_publication_request(request_name: str, reason: str) -> dict:
	return submission.reject_publication_request(request_name, reason)


@frappe.whitelist()
def approve_first_release(release_name: str) -> dict:
	return publishing.approve_first_release(release_name)


@frappe.whitelist()
def reject_first_release(release_name: str, reason: str) -> dict:
	return publishing.reject_first_release(release_name, reason)


@frappe.whitelist()
def request_release_check(plugin_name: str) -> dict:
	from builder_hub.plugins.tasks import request_release_check as enqueue_check

	return enqueue_check(plugin_name)


@frappe.whitelist()
def yank_release(release_name: str) -> dict:
	return publishing.yank_release(release_name)


@frappe.whitelist()
def block_release(release_name: str) -> dict:
	return publishing.block_release(release_name)


@frappe.whitelist()
def block_plugin(plugin_name: str) -> dict:
	return publishing.block_plugin(plugin_name)


@frappe.whitelist()
def block_publisher(publisher_id: str) -> dict:
	return publishing.block_publisher(publisher_id)


def _public_plugin(plugin_name: str):
	if not isinstance(plugin_name, str) or not PLUGIN_NAME_PATTERN.fullmatch(plugin_name):
		_not_found()
	row = frappe.db.get_value(
		"Hub Plugin",
		plugin_name,
		[*_plugin_fields(), "readme"],
		as_dict=True,
	)
	if not row or row.status not in {"Published", "Deprecated"}:
		_not_found()
	return row


def _latest_release(plugin_name: str, protocol_version: int):
	releases = frappe.get_all(
		"Hub Plugin Release",
		filters={
			"plugin": plugin_name,
			"status": "Published",
			"protocol_version": ("<=", protocol_version),
		},
		fields=["version", "protocol_version", "package_size", "package_sha256", "published_on"],
		ignore_permissions=True,
	)
	return max(releases, key=lambda row: semver_key(row.version), default=None)


def _catalog_item(plugin, publisher, release, base_url: str, *, include_latest: bool = True) -> dict:
	item = {
		"name": plugin.plugin_name,
		"label": plugin.label,
		"description": plugin.description,
		"publisher": {
			"id": publisher.publisher_id,
			"name": publisher.display_name,
			"verified": bool(publisher.verified),
		},
		"repository_url": plugin.repository_url,
		"license": plugin.license,
		"categories": _json(plugin.categories, []),
		"icon": _absolute_url(plugin.icon, base_url),
		"status": plugin.status,
		"replacement": plugin.replacement or None,
	}
	if include_latest:
		item["latest_release"] = {
			"version": release.version,
			"protocol_version": release.protocol_version,
			"package_size": release.package_size,
			"package_sha256": release.package_sha256,
			"published_on": _iso(release.published_on),
		}
	return item


def _publisher(name: str):
	return frappe.db.get_value(
		"Hub Publisher",
		name,
		["publisher_id", "display_name", "verified", "status"],
		as_dict=True,
	)


def _plugin_fields() -> list[str]:
	return [
		"name",
		"plugin_name",
		"publisher",
		"label",
		"description",
		"repository_url",
		"license",
		"categories",
		"icon",
		"status",
		"replacement",
	]


def _protocol_version(value) -> int:
	try:
		value = int(value)
	except (TypeError, ValueError):
		frappe.throw(_("protocol_version must be a positive integer."))
	if value < 1 or value > 2_147_483_647:
		frappe.throw(_("protocol_version must be a positive integer."))
	return value


def _page(value) -> int:
	try:
		value = int(value)
	except (TypeError, ValueError):
		frappe.throw(_("page must be a positive integer."))
	if value < 1:
		frappe.throw(_("page must be a positive integer."))
	return value


def _validate_identity(plugin_name, version) -> None:
	if not isinstance(plugin_name, str) or not PLUGIN_NAME_PATTERN.fullmatch(plugin_name):
		frappe.throw(_("Invalid plugin name."))
	if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
		frappe.throw(_("Invalid release version."))


def _absolute_url(path: str | None, base_url: str) -> str | None:
	if path and path.startswith("/"):
		return base_url.rstrip("/") + path
	return path


def _iso(value) -> str | None:
	if not value:
		return None
	date = get_datetime(value)
	if date.tzinfo is None:
		date = date.replace(tzinfo=UTC)
	return date.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _json(value, default):
	if value in (None, ""):
		return default
	if isinstance(value, str):
		try:
			return json.loads(value)
		except json.JSONDecodeError:
			return default
	return value


def _not_found():
	frappe.throw(_("Plugin or release not found."), frappe.DoesNotExistError)
