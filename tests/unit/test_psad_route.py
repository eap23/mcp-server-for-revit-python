# -*- coding: utf-8 -*-
"""Unit tests for the PSAD route helper."""

from revit_mcp.psad_exclude_pipes_route import (
    handle_exclude_mainline_pipes_request,
)


def test_non_object_request_returns_wrapper_style_error():
    payload, status_code = handle_exclude_mainline_pipes_request(
        object(),
        [1, 2, 3],
    )

    assert status_code == 200
    assert payload == {
        "status": "error",
        "error": "request_must_be_object",
    }


def test_non_list_element_ids_returns_wrapper_style_error():
    payload, status_code = handle_exclude_mainline_pipes_request(
        object(),
        {"element_ids": "1,2,3"},
    )

    assert status_code == 200
    assert payload == {
        "status": "error",
        "error": "element_ids_must_be_list",
    }


def test_invalid_json_returns_structured_error():
    payload, status_code = handle_exclude_mainline_pipes_request(
        object(),
        "{invalid-json}",
    )

    assert status_code == 200
    assert payload["status"] == "error"
    assert payload["error"] == "invalid_json"


def test_no_active_document_returns_structured_error():
    payload, status_code = handle_exclude_mainline_pipes_request(
        None,
        {"element_ids": []},
    )

    assert status_code == 200
    assert payload == {
        "status": "error",
        "error": "no_active_document",
    }


def test_valid_payload_delegates_to_workflow_unchanged():
    expected = {
        "workflow": "piping.exclude_mainline_from_schedules",
        "status": "ok",
        "input_count": 2,
        "updated_count": 1,
        "skipped_invalid_ids": [],
        "skipped_missing_elements": [],
        "skipped_non_pipe_ids": [2],
        "skipped_missing_parameter_ids": [],
    }

    def invoke_workflow(doc, payload):
        assert doc == "doc"
        assert payload == {"element_ids": [1, 2]}
        return expected

    payload, status_code = handle_exclude_mainline_pipes_request(
        "doc",
        {"element_ids": [1, 2]},
        invoke_workflow=invoke_workflow,
    )

    assert status_code == 200
    assert payload is expected


def test_empty_list_passthrough_supports_no_op():
    def invoke_workflow(doc, payload):
        assert payload == {"element_ids": []}
        return {"status": "no_op", "input_count": 0, "updated_count": 0}

    payload, status_code = handle_exclude_mainline_pipes_request(
        "doc",
        {"element_ids": []},
        invoke_workflow=invoke_workflow,
    )

    assert status_code == 200
    assert payload["status"] == "no_op"
