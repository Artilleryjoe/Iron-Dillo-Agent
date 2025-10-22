"""Seed the Cybersandbox vault with sanitized demo documents."""

from __future__ import annotations

import json

from ..backend.settings import get_settings

DEMO_DOCS = {
    "CLIENT_001_policy.md": """# CLIENT_001 Security Policy\n\nAll remote access must use MFA. Weekly patch windows occur on Tuesdays. Incident hotline: CLIENT_NAME-SECURE.""",
    "CLIENT_002_incident.txt": """2024-05-01 13:22Z CLIENT_002 reported phishing attempts from example.net. Blocked IP: 203.0.113.4.""",
    "CLIENT_003_audit.md": """Findings:\n- Missing asset inventory updates\n- Legacy firewall rules allow broad CIDR 10.0.0.0/8""",
}


def main() -> None:
    settings = get_settings()
    vault = settings.sanitized_docs_path
    for filename, content in DEMO_DOCS.items():
        path = vault / filename
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path}")

    manifest = vault / "demo_manifest.json"
    manifest.write_text(json.dumps(sorted(DEMO_DOCS.keys()), indent=2), encoding="utf-8")
    print(f"Manifest saved to {manifest}")


if __name__ == "__main__":
    main()
