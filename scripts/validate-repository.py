from pathlib import Path

for name in ("browser-history", "loan-disbursement", "transaction-processor"):
    path = Path(name) / "README.md"
    text = path.read_text()
    assert text.strip().startswith("# "), f"Missing title: {path}"
    opened = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            opened = None if opened else "```"
    assert opened is None, f"Unclosed code fence: {path}"
    print(f"PASS: Assessment prompt structure: {path}")
