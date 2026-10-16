import re
from pathlib import Path

CSS_PATH = Path(__file__).resolve().parent.parent / "app" / "static" / "css" / "dashboard.css"
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(")
ROOT = re.compile(r":root\s*\{[^}]*\}")
DARK = re.compile(
    r"@media \(prefers-color-scheme: dark\)\s*\{(?P<body>(?:[^{}]*\{[^{}]*\})*[^{}]*)\}"
)


def _css():
    return CSS_PATH.read_text(encoding="utf-8")


def _dark_body():
    match = DARK.search(_css())
    assert match is not None, "falta el bloque prefers-color-scheme: dark"
    return match.group("body")


def test_dashboard_css_has_dark_scheme_block():
    assert "prefers-color-scheme: dark" in _css()
    assert _dark_body().strip()


def test_dark_block_uses_design_tokens():
    body = _dark_body().lower()
    for token in ("#0b0d12", "#13161d", "#1b1f29", "#262b36", "#edeae2", "#8a8f9c"):
        assert token in body


def test_dark_block_redefines_core_variables():
    body = _dark_body()
    for name in (
        "--ds-bg", "--ds-surface", "--ds-surface-alt", "--ds-border",
        "--ds-text", "--ds-text-secondary", "--ds-text-muted", "--ds-primary",
    ):
        assert name + ":" in body


def test_color_scheme_declared():
    assert "color-scheme: light dark" in _css()


def test_no_hardcoded_colors_outside_tokens():
    css = DARK.sub("", _css())
    css = ROOT.sub("", css)
    offenders = []
    for line in css.splitlines():
        if "::backdrop" in line or "var(--ds-text-secondary,#64748b)" in line:
            continue
        if COLOR.search(line):
            offenders.append(line.strip())
    assert offenders == []