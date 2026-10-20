"""Optional MCP server exposing the same support operations via FastMCP.

Run:  python -m agentic.tools.mcp_server      (stdio transport)
The LangGraph workflow calls the tools in-process (agentic/tools/tools.py); this server exposes the
identical service layer so any MCP client (Claude Desktop, other agents) can reuse it.
"""
from fastmcp import FastMCP

from agentic.tools import cultpass_db as db

mcp = FastMCP("cultpass-support-tools")

for _fn in (db.lookup_account, db.get_subscription_status, db.cancel_subscription,
            db.list_reservations, db.cancel_reservation, db.process_refund, db.check_refund_eligibility):
    mcp.tool(_fn)

if __name__ == "__main__":
    mcp.run()
