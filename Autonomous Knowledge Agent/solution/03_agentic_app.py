"""Run UDA-Hub from the command line.

    python 03_agentic_app.py                       # interactive chat (anonymous customer)
    python 03_agentic_app.py --user u_alice        # chat as an authenticated CultPass customer
    python 03_agentic_app.py --demo                # run the scripted demo scenarios and print results
Databases are created automatically on first run if missing (same code as notebooks 01 and 02).
"""
import argparse

from agentic import config
from agentic.workflow import create_app, inspect_thread, run_ticket
from data.setup_db import setup_core_db, setup_external_db
from utils import chat_interface, show

DEMO = [
    ("KB resolution", None, ["How do I reset my password?"]),
    ("Escalation: nothing in KB", None, ["Do you sell gift cards for my cat?"]),
    ("Account action, multi-turn", None, ["Please cancel my subscription", "bob@example.com", "yes"]),
    ("Refund needing approval", "u_dev", ["I want a refund"]),
    ("Security risk", None, ["Someone hacked my account and made unauthorized charges!"]),
    ("Returning customer (long-term memory)", "u_alice", ["How do I reset my password? Please keep it short.",
                                                         "__NEW__", "I forgot my password again, what do I do?"]),
]


def ensure_databases():
    if not config.cultpass_db_path().exists():
        setup_external_db()
    if not config.udahub_db_path().exists():
        setup_core_db()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", help="external (CultPass) user id, e.g. u_alice")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    ensure_databases()
    app = create_app()
    if not args.demo:
        return chat_interface(app, external_user_id=args.user)
    for title, user, turns in DEMO:
        print(f"=== {title} ===")
        thread = None
        for t in turns:
            if t == "__NEW__":
                thread = None
                continue
            out = run_ticket(app, t, thread, external_user_id=user)
            thread = out["thread_id"]
            show(out, t)


if __name__ == "__main__":
    main()
