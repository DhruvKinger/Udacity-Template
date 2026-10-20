"""Helpers for notebooks / CLI: interactive chat loop, pretty printing."""
from __future__ import annotations

from agentic.workflow import inspect_thread, run_ticket

HELP = "commands: /quit  /new (new ticket)  /state (inspect thread)  /tools (tool usage)"


def chat_interface(app, thread_id: str | None = None, external_user_id: str | None = None, channel: str = "chat"):
    """Simple interactive loop. The same thread_id keeps the session (short-term memory)."""
    print("UDA-Hub support chat.", HELP)
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/new":
            thread_id = None
            print("(new ticket)")
            continue
        if text in ("/state", "/tools"):
            if not thread_id:
                print("(no session yet)")
                continue
            info = inspect_thread(app, thread_id)
            print(info["tool_usage"] if text == "/tools" else {k: info[k] for k in ("ticket_id", "classification", "resolution", "pending_action")})
            continue
        out = run_ticket(app, text, thread_id, external_user_id=external_user_id, channel=channel)
        thread_id = out["thread_id"]
        print(f"[{out.get('route')} | {out['resolution'].get('status')} | ticket {out['ticket_id']}]")
        print(f"Agent: {out['final_response']}\n")


def show(out: dict, user_text: str | None = None):
    if user_text:
        print(f"CUSTOMER: {user_text}")
    print(f"  route={out.get('route')} ({out.get('route_reason')}) status={out['resolution'].get('status')} "
          f"confidence={out['resolution'].get('confidence')}")
    print(f"  AGENT: {out['final_response']}\n")
