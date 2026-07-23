# -*- coding: utf-8 -*-
"""Unit tests for PSAD MCP tool registration and forwarding."""

import importlib
import importlib.util

import pytest

from tools.psad_tools import register_psad_tools


@pytest.fixture
def psad_tools(mock_mcp, mock_revit_get, mock_revit_post, mock_revit_image):
    mock_revit_post.return_value = {
        "workflow": "piping.exclude_mainline_from_schedules",
        "status": "ok",
        "input_count": 2,
        "updated_count": 1,
        "skipped_invalid_ids": [],
        "skipped_missing_elements": [],
        "skipped_non_pipe_ids": [2],
        "skipped_missing_parameter_ids": [],
    }
    register_psad_tools(mock_mcp, mock_revit_get, mock_revit_post, mock_revit_image)
    return mock_mcp.tools


def test_tool_is_registered(psad_tools):
    assert "psad_exclude_mainline_pipes_from_schedules" in psad_tools


async def test_tool_forwards_payload_unchanged(psad_tools, mock_revit_post):
    result = await psad_tools["psad_exclude_mainline_pipes_from_schedules"](
        element_ids=[1, 2],
        ctx=None,
    )

    mock_revit_post.assert_called_once_with(
        "/psad/exclude-mainline-pipes/",
        {"element_ids": [1, 2]},
        None,
    )
    assert result["status"] == "ok"
    assert result["updated_count"] == 1


async def test_tool_supports_empty_lists(psad_tools, mock_revit_post):
    await psad_tools["psad_exclude_mainline_pipes_from_schedules"](
        element_ids=[],
        ctx=None,
    )

    mock_revit_post.assert_called_once_with(
        "/psad/exclude-mainline-pipes/",
        {"element_ids": []},
        None,
    )


@pytest.mark.skipif(
    importlib.util.find_spec("rvt_bimdex_mcp") is None,
    reason="External BIMDEX editable install is not available in this test environment.",
)
def test_can_import_exclude_pipes_wrapper():
    module = importlib.import_module("rvt_bimdex_mcp.exclude_pipes")

    assert module.MCP_TOOL_NAME == "psad_exclude_mainline_pipes_from_schedules"
    assert module.WORKFLOW_KEY == "piping.exclude_mainline_from_schedules"
