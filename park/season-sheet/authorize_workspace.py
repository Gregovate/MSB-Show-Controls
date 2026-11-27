"""Run once on a laptop to authorize the MSB Workspace spreadsheet uploader."""
import argparse
import json
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("desktop_client", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    flow = InstalledAppFlow.from_client_secrets_file(
        str(args.desktop_client), ["https://www.googleapis.com/auth/spreadsheets"])
    # Loopback keeps the interactive browser sign-in on the operator's laptop.
    credentials = flow.run_local_server(host="127.0.0.1", port=0, prompt="consent")
    if not credentials.refresh_token:
        raise RuntimeError("Google did not issue an offline refresh token")
    info = json.loads(credentials.to_json())
    info["type"] = "authorized_user"
    with os.fdopen(os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "w") as output:
        json.dump(info, output)
    print("Saved the HA credential to", args.output)


if __name__ == "__main__":
    main()
