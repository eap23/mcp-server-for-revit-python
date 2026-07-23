# -*- coding: utf-8 -*-
"""Integration tests for the PSAD exclude-pipes route."""

import os

import httpx
import pytest

BASE_URL = "http://localhost:48884/revit_mcp"


@pytest.mark.integration
async def test_psad_route_rejects_non_object_payload(revit_ready):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/psad/exclude-mainline-pipes/",
            json=[1, 2, 3],
        )

    if response.status_code == 404:
        pytest.skip("PSAD route not registered in the active pyRevit extension")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"] == "request_must_be_object"


@pytest.mark.integration
async def test_psad_route_rejects_non_list_element_ids(revit_ready):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/psad/exclude-mainline-pipes/",
            json={"element_ids": "1,2,3"},
        )

    if response.status_code == 404:
        pytest.skip("PSAD route not registered in the active pyRevit extension")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"] == "element_ids_must_be_list"


@pytest.mark.integration
async def test_psad_route_rejects_invalid_json(revit_ready):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/psad/exclude-mainline-pipes/",
            content="{invalid-json}",
            headers={"Content-Type": "application/json"},
        )

    if response.status_code == 404:
        pytest.skip("PSAD route not registered in the active pyRevit extension")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"] == "invalid_json"


@pytest.mark.integration
async def test_psad_route_happy_path_requires_configured_pipe_ids(
    revit_ready,
    revit_post,
    test_file_path,
):
    raw_ids = os.environ.get("PSAD_TEST_PIPE_IDS", "").strip()
    if not raw_ids:
        pytest.skip("Set PSAD_TEST_PIPE_IDS to run the live PSAD workflow test")

    element_ids = [int(value.strip()) for value in raw_ids.split(",") if value.strip()]

    await revit_post("/open_document/", {"file_path": test_file_path})
    try:
        response = await revit_post(
            "/psad/exclude-mainline-pipes/",
            {"element_ids": element_ids},
        )

        if isinstance(response, str) and "RouteHandlerNotDefined" in response:
            pytest.skip("PSAD route not registered in the active pyRevit extension")

        if (
            isinstance(response, dict)
            and response.get("error") == "workflow_import_failed"
        ):
            pytest.skip(
                "External BIMDEX wrapper is not installed in the active Revit runtime"
            )

        assert isinstance(response, dict)
        assert response["status"] == "ok"
        assert response["updated_count"] > 0
        assert response["input_count"] == len(element_ids)
    finally:
        await revit_post("/close_document/", {"save": False})
