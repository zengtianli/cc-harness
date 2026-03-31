"""Output six-dimension score table."""

from datetime import date


def render_scorecard(results: dict) -> str:
    """Render the six-dimension score card as markdown."""
    dimensions = results.get("dimensions", [])
    today = date.today().isoformat()

    lines = [
        f"## Harness Score Card -- {today}",
        "",
        "| 维度 | 分数 | 关键发现 |",
        "|------|------|---------|",
    ]

    total = 0.0
    for dim in dimensions:
        score = dim["score"]
        total += score
        # Summarize top finding
        top_finding = ""
        for f in dim.get("findings", []):
            if f["severity"] in ("critical", "warning"):
                top_finding = f["title"]
                break
        if not top_finding and dim.get("findings"):
            top_finding = dim["findings"][0].get("title", "")

        lines.append(f"| {dim['dimension']} | {score}/10 | {top_finding} |")

    avg = round(total / len(dimensions), 1) if dimensions else 0.0
    lines.append(f"| **总分** | **{avg}/10** | |")
    lines.append("")

    return "\n".join(lines)
