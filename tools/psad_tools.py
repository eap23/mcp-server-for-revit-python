# -*- coding: utf-8 -*-
"""PSAD-specific MCP tools."""

from mcp.server.fastmcp import Context


def register_psad_tools(mcp, revit_get, revit_post, revit_image=None):
    """Register PSAD tools with the MCP server."""

    @mcp.tool()
    async def psad_exclude_mainline_pipes_from_schedules(
        element_ids: list[int],
        ctx: Context = None,
    ):
        """Exclude the specified mainline pipe elements from schedules."""
        payload = {"element_ids": element_ids}
        return await revit_post("/psad/exclude-mainline-pipes/", payload, ctx)
