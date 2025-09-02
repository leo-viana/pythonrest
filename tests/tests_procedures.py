# tests_procedures.py
# Calls /sql/storedprocedure for multiple stored procedure patterns on the generated API.
# Notes:
# - Header: StoredProcedure: <procedure_name>
# - Body: { "in": [...], "out": <number_of_out_slots> }
# - For current SQL Server implementation, "out" just fills positional OUT slots with NULL and outputs are not captured.

import json
import os
import sys
from typing import List, Optional

import requests

BASE_URL = os.getenv("PYTHONREST_BASE_URL", "http://localhost:5000")
ENDPOINT = f"{BASE_URL}/sql/storedprocedure"
HEADERS_JSON = {"Content-Type": "application/json"}
TIMEOUT = int(os.getenv("PYTHONREST_TIMEOUT", "60"))


def call_proc(proc_name: str, in_params: Optional[List] = None, out_count: int = 0) -> None:
    body = {
        "in": in_params or [],
        "out": out_count or 0
    }
    headers = {
        **HEADERS_JSON,
        "StoredProcedure": proc_name
    }

    print(f"\n== {proc_name} ==")
    print(f"POST {ENDPOINT}")
    print("Header StoredProcedure:", proc_name)
    print("Body:", json.dumps(body, ensure_ascii=False))

    try:
        resp = requests.post(ENDPOINT, headers=headers, json=body, timeout=TIMEOUT)
        print(f"Status: {resp.status_code}")
        try:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(resp.text)
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    # No parameters
    call_proc("sp_GetDatabaseStats")

    # IN parameter only
    call_proc("sp_GetUserPosts", in_params=["john_doe"])

    # Multiple IN parameters (with defaults supported by procedure)
    call_proc("sp_GetPostsByDateRange", in_params=["2024-01-01", "2024-12-31", 50])

    # OUT parameters only (will pass NULL placeholders; outputs are not captured)
    call_proc("sp_GetDatabaseInfo", in_params=[], out_count=3)

    # IN and OUT parameters
    call_proc("sp_GetUserStats", in_params=["john_doe"], out_count=4)

    # INOUT (treated as OUT slot placeholder, not captured)
    call_proc("sp_UpdateUserJoinDate", in_params=["john_doe"], out_count=1)

    # Table-valued parameter simulation as JSON string
    tvp_json = '[{"username":"user1","id":"uuid1"},{"username":"user2","id":"uuid2"}]'
    call_proc("sp_BulkInsertUsers", in_params=[tvp_json])

    # Default parameters with multiple INs
    call_proc("sp_SearchPosts", in_params=["hello world", 1, 1, 25])

    # Error handling and validation (OUT placeholders, not captured)
    call_proc("sp_CreateUser", in_params=["new_user", "my-new-uuid"], out_count=2)

    # Dynamic SQL with parameters
    call_proc("sp_GetTopUsers", in_params=["followers", 20])

    # Cursor with OUTPUT parameter (placeholder only)
    call_proc("sp_ProcessAllUsers", in_params=[], out_count=1)

    # Temporary tables with default parameter
    call_proc("sp_GetUserActivityReport", in_params=["john_doe", 7])

    # Table variables with default parameter
    call_proc("sp_GetUserNetwork", in_params=["john_doe", 3])


if __name__ == "__main__":
    # Simple check for requests dependency
    try:
        import requests  # noqa: F401
    except Exception:
        print("This script requires 'requests'. Install with: pip install requests")
        sys.exit(1)

    main()