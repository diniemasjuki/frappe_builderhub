"""Public plugin publication requests and maintainer review."""

from __future__ import annotations

import re
from dataclasses import dataclass

import frappe
from frappe import _
from frappe.utils import now_datetime

from builder_hub.plugins.github import (
	GitHubClient,
	get_repository_contract,
	get_repository_license,
	get_validated_repository_url,
	parse_repository_url,
	validate_public_repository,
)
from builder_hub.plugins.protocol import ProtocolValidationError
from builder_hub.plugins.publishing import (
	ValidatedReleaseImport,
	approve_first_release,
	import_validated_release,
	require_maintainer,
	validate_release_source,
)

CATEGORY = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")
# A maintainer reviews these values. Approval refuses a release that changed them.
REVIEWED_FIELDS = (
	"plugin_name",
	"publisher_id",
	"github_account_id",
	"github_repository_id",
	"license",
	"version",
	"github_release_id",
	"github_asset_id",
	"package_sha256",
)


@dataclass(frozen=True)
class ValidatedPublication:
	repository: dict
	publisher_id: str
	publisher_name: str
	license_id: str
	categories: list[str]
	release: ValidatedReleaseImport


def request_publication(
	repository_url: str,
	categories: list[str] | str | None = None,
	*,
	client: GitHubClient | None = None,
) -> dict:
	"""Validate a public repository and create one maintainer review request."""
	try:
		publication = validate_publication(
			repository_url,
			validate_categories(categories),
			client=client,
		)
		request_name = get_open_request(publication)
		assert_identity_available(publication, request_name)
	except ProtocolValidationError as error:
		frappe.throw(_(error.message))

	request = save_request(publication, request_name)
	return {
		"request": request.name,
		"plugin_name": request.plugin_name,
		"status": request.status,
	}


def validate_publication(
	repository_url: str,
	categories: list[str],
	*,
	client: GitHubClient | None = None,
) -> ValidatedPublication:
	client = client or GitHubClient()
	owner_name, repository_name = parse_repository_url(repository_url)
	repository = client.get_repository_by_name(owner_name, repository_name)
	owner = repository.get("owner") or {}
	owner_id = str(owner.get("id") or "")
	owner_login = owner.get("login") or ""
	if not owner_id or not owner_login:
		raise ProtocolValidationError("invalid_repository", "GitHub returned an invalid repository owner.")
	validate_public_repository(repository)

	license_id = get_repository_license(repository)
	contract = get_repository_contract(client, repository, license_id)
	manifest = contract["manifest"]
	publisher_id, publisher_name = resolve_publisher(owner_id, owner_login)
	if manifest["name"].split("/", 1)[0] != publisher_id:
		raise ProtocolValidationError(
			"publisher_owner_mismatch",
			f"Manifest name must use the repository owner's {publisher_id} namespace.",
		)
	release = validate_release_source(
		client,
		repository,
		contract,
		manifest["name"],
		manifest["version"],
	)
	return ValidatedPublication(
		repository=repository,
		publisher_id=publisher_id,
		publisher_name=publisher_name,
		license_id=license_id,
		categories=categories,
		release=release,
	)


def approve_publication_request(
	request_name: str,
	reason: str | None = None,
	*,
	client: GitHubClient | None = None,
) -> dict:
	require_maintainer()
	request = frappe.get_doc("Hub Publication Request", request_name)
	if request.status != "Pending Review":
		frappe.throw(_("Only a pending publication request can be approved."))
	try:
		publication = validate_publication(
			request.repository_url,
			validate_categories(request.categories),
			client=client,
		)
		assert_request_unchanged(request, publication)
	except ProtocolValidationError as error:
		frappe.throw(_(error.message))

	create_or_update_publisher(publication)
	plugin = create_listing(publication)
	release = import_validated_release(plugin.name, publication.release, first_release=True)
	if release.status != "Pending Review":
		frappe.throw(_("The first release could not be prepared for review."))
	result = approve_first_release(release.name)
	save_review(request, "Approved", reason, published_plugin=plugin.name, published_release=release.name)
	return {"request": request.name, **result}


def reject_publication_request(request_name: str, reason: str) -> dict:
	require_maintainer()
	if not reason or not reason.strip():
		frappe.throw(_("A rejection reason is required."))
	request = frappe.get_doc("Hub Publication Request", request_name)
	if request.status != "Pending Review":
		frappe.throw(_("Only a pending publication request can be rejected."))
	save_review(request, "Rejected", reason.strip())
	return {"request": request.name, "status": request.status}


def save_review(request, status: str, reason: str | None, **values) -> None:
	request.update(
		{
			"status": status,
			"review_reason": reason,
			"reviewed_by": frappe.session.user,
			"reviewed_on": now_datetime(),
			**values,
		}
	)
	request.save(ignore_permissions=True)


def get_open_request(publication: ValidatedPublication) -> str | None:
	"""A pending or rejected request for the repository, which a new submission replaces."""
	return frappe.db.get_value(
		"Hub Publication Request",
		{"github_repository_id": str(publication.repository["id"]), "status": ("!=", "Approved")},
		"name",
	)


def save_request(publication: ValidatedPublication, request_name: str | None):
	values = get_request_values(publication)
	if not request_name:
		return frappe.get_doc({"doctype": "Hub Publication Request", **values}).insert(
			ignore_permissions=True
		)
	request = frappe.get_doc("Hub Publication Request", request_name)
	request.update({**values, "review_reason": None, "reviewed_by": None, "reviewed_on": None})
	return request.save(ignore_permissions=True)


def get_request_values(publication: ValidatedPublication) -> dict:
	release = publication.release
	package = release.package
	return {
		"repository_url": get_validated_repository_url(publication.repository),
		"plugin_name": package.manifest["name"],
		"publisher_id": publication.publisher_id,
		"publisher_name": publication.publisher_name,
		"github_owner": publication.repository["owner"]["login"],
		"github_account_id": str(publication.repository["owner"]["id"]),
		"github_repository_id": str(publication.repository["id"]),
		"license": publication.license_id,
		"categories": frappe.as_json(publication.categories),
		"version": package.manifest["version"],
		"manifest": frappe.as_json(package.manifest),
		"readme": release.contract["readme"],
		"github_release_url": release.release_data["html_url"],
		"github_release_id": str(release.release_data["id"]),
		"github_asset_id": str(release.asset["id"]),
		"package_url": release.asset["browser_download_url"],
		"package_size": package.package_size,
		"package_sha256": package.package_sha256,
		"release_notes": release.release_data.get("body") or "",
		"status": "Pending Review",
	}


def create_or_update_publisher(publication: ValidatedPublication):
	owner = publication.repository["owner"]
	if frappe.db.exists("Hub Publisher", publication.publisher_id):
		publisher = frappe.get_doc("Hub Publisher", publication.publisher_id)
		publisher.github_owner = owner["login"]
		publisher.verified = 1
		publisher.status = "Active"
		publisher.save(ignore_permissions=True)
		return publisher
	return frappe.get_doc(
		{
			"doctype": "Hub Publisher",
			"publisher_id": publication.publisher_id,
			"display_name": publication.publisher_name,
			"github_owner": owner["login"],
			"github_account_id": str(owner["id"]),
			"verified": 1,
			"status": "Active",
		}
	).insert(ignore_permissions=True)


def create_listing(publication: ValidatedPublication):
	manifest = publication.release.package.manifest
	return frappe.get_doc(
		{
			"doctype": "Hub Plugin",
			"plugin_name": manifest["name"],
			"publisher": publication.publisher_id,
			"label": manifest["label"],
			"description": manifest["description"],
			"readme": publication.release.contract["readme"],
			"repository_url": get_validated_repository_url(publication.repository),
			"github_repository_id": str(publication.repository["id"]),
			"license": publication.license_id,
			"categories": frappe.as_json(publication.categories),
			"status": "Pending Review",
		}
	).insert(ignore_permissions=True)


def assert_identity_available(
	publication: ValidatedPublication,
	request_name: str | None = None,
) -> None:
	plugin_name = publication.release.package.manifest["name"]
	repository_id = str(publication.repository["id"])
	if frappe.db.exists("Hub Plugin", plugin_name):
		raise ProtocolValidationError("plugin_exists", "This plugin name has already been used.")
	if frappe.db.exists("Hub Plugin", {"github_repository_id": repository_id}):
		raise ProtocolValidationError(
			"repository_exists", "This GitHub repository has already been published."
		)
	for filters, message in (
		({"plugin_name": plugin_name}, "A publication request already uses this plugin name."),
		({"github_repository_id": repository_id}, "This GitHub repository was already submitted."),
	):
		existing = frappe.db.get_value("Hub Publication Request", filters, "name")
		if existing and existing != request_name:
			raise ProtocolValidationError("request_exists", message)


def assert_request_unchanged(request, publication: ValidatedPublication) -> None:
	assert_identity_available(publication, request.name)
	values = get_request_values(publication)
	if any(request.get(fieldname) != values[fieldname] for fieldname in REVIEWED_FIELDS):
		raise ProtocolValidationError(
			"publication_changed",
			"The repository or release changed after submission. Submit the repository again.",
		)


def resolve_publisher(owner_id: str, owner_login: str) -> tuple[str, str]:
	publisher_id = frappe.db.get_value("Hub Publisher", {"github_account_id": owner_id}, "publisher_id")
	if not publisher_id:
		publisher_id = owner_login.lower()
		if frappe.db.exists("Hub Publisher", publisher_id):
			raise ProtocolValidationError(
				"publisher_owner_mismatch",
				"The repository owner belongs to a different GitHub account.",
			)
		return publisher_id, owner_login

	publisher = frappe.get_doc("Hub Publisher", publisher_id)
	if publisher.status == "Blocked":
		raise ProtocolValidationError("publisher_blocked", "This publisher is blocked.")
	return publisher.publisher_id, publisher.display_name


def validate_categories(categories: list[str] | str | None) -> list[str]:
	if categories in (None, ""):
		categories = []
	elif isinstance(categories, str):
		try:
			categories = frappe.parse_json(categories)
		except ValueError:
			categories = None
	if not isinstance(categories, list) or len(categories) > 20 or len(categories) != len(set(categories)):
		frappe.throw(_("Categories must be a unique list with at most 20 values."))
	if any(not isinstance(item, str) or not CATEGORY.fullmatch(item) for item in categories):
		frappe.throw(_("Each category must be a lowercase ID."))
	return categories
