# -*- coding: UTF-8 -*-
"""PSAD exclude-mainline-pipes route for Revit MCP."""

import json
import logging

try:
    from pyrevit import routes
except ImportError:
    routes = None

logger = logging.getLogger(__name__)


def _parse_request_payload(request_data):
    """Parse request data into a Python object."""
    if isinstance(request_data, str):
        try:
            return json.loads(request_data), None
        except Exception as exc:
            logger.warning("Failed to parse PSAD request JSON: %s", str(exc))
            return None, {
                "status": "error",
                "error": "invalid_json",
                "details": str(exc),
            }

    return request_data, None


def _validate_payload(payload):
    """Validate payload shape before invoking the external workflow."""
    if not isinstance(payload, dict):
        return {
            "status": "error",
            "error": "request_must_be_object",
        }

    if not isinstance(payload.get("element_ids"), list):
        return {
            "status": "error",
            "error": "element_ids_must_be_list",
        }

    return None


def _load_invoke_exclude_mainline_pipes():
    """Load the external BIMDEX wrapper lazily."""
    from rvt_bimdex_mcp.exclude_pipes import invoke_exclude_mainline_pipes

    return invoke_exclude_mainline_pipes


def handle_exclude_mainline_pipes_request(
    doc,
    request_data,
    invoke_workflow=None,
):
    """Handle the route request and return a JSON payload plus HTTP status."""
    payload, parse_error = _parse_request_payload(request_data)
    if parse_error:
        return parse_error, 200

    validation_error = _validate_payload(payload)
    if validation_error:
        return validation_error, 200

    if doc is None:
        return {
            "status": "error",
            "error": "no_active_document",
        }, 200

    if invoke_workflow is None:
        try:
            invoke_workflow = _load_invoke_exclude_mainline_pipes()
        except Exception as exc:
            logger.error("Failed to import PSAD workflow wrapper: %s", str(exc))
            return {
                "status": "error",
                "error": "workflow_import_failed",
                "details": str(exc),
            }, 200

    try:
        workflow_result = invoke_workflow(doc, payload)
    except Exception as exc:
        logger.exception("PSAD workflow invocation failed")
        return {
            "status": "error",
            "error": "workflow_invocation_failed",
            "details": str(exc),
        }, 200

    if isinstance(workflow_result, dict):
        return workflow_result, 200

    logger.error(
        "PSAD workflow returned unsupported response type: %s",
        type(workflow_result).__name__,
    )
    return {
        "status": "error",
        "error": "workflow_response_must_be_object",
        "details": type(workflow_result).__name__,
    }, 200


def register_psad_routes(api):
    """Register PSAD-specific routes with the API."""

    @api.route("/psad/exclude-mainline-pipes/", methods=["POST"])
    def exclude_mainline_pipes(doc, request):
        payload, status_code = handle_exclude_mainline_pipes_request(
            doc,
            getattr(request, "data", None),
        )
        return routes.make_response(data=payload, status=status_code)

    logger.info("PSAD routes registered successfully")
