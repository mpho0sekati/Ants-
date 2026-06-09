"""
tools/__init__.py — Ant tools, now powered by real ImmuniSOC-Nexus engines.

Protector tools use:
  • immunisoc.tcell     — T-Cell engine (Low/Medium/High/Critical containment)
  • immunisoc.deception — Honeytoken detection
  • ant_behavior        — Protector decision logic from ants_simulation.py
"""

from crewai_tools import tool


# ── Collector tools ───────────────────────────────────────────────────────────

@tool
def web_search(query: str) -> str:
    """Search the web for information on a topic.
    Params: query — the search query string.
    """
    return (
        f"[web_search stub] '{query}': set SERPAPI_KEY in .env for real results. "
        "Use your knowledge to reason about the query."
    )


@tool
def read_file(path: str) -> str:
    """Read the contents of a local text file.
    Params: path — file path to read.
    """
    import os
    if not os.path.exists(path):
        return f"File not found: {path}"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(8000)


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a local file (creates or overwrites).
    Params: path — file path; content — text to write.
    """
    import os
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Written {len(content)} chars to {path}"


# ── Scout tools ───────────────────────────────────────────────────────────────

@tool
def list_directory(path: str) -> str:
    """List files and folders in a directory.
    Params: path — directory to list.
    """
    import os
    if not os.path.isdir(path):
        return f"Not a directory: {path}"
    entries = [
        f"  [{'DIR' if e.is_dir() else 'FILE'}] {e.name}"
        for e in os.scandir(path)
    ]
    return "\n".join(entries) or "(empty)"


@tool
def run_python(code: str) -> str:
    """Run a small Python snippet and return stdout.
    Params: code — Python source (max 50 lines). Safe, non-destructive only.
    """
    import io, sys, textwrap
    if len(code.splitlines()) > 50:
        return "❌  Too long (> 50 lines)."
    buf = io.StringIO()
    old = sys.stdout; sys.stdout = buf
    try:
        exec(textwrap.dedent(code), {})   # noqa: S102
    except Exception as e:
        return f"❌  Error: {e}"
    finally:
        sys.stdout = old
    return buf.getvalue() or "(no output)"


# ── Protector tools — powered by real ImmuniSOC engines ───────────────────────

@tool
def tcell_scan(ant_id: str, role: str, text: str) -> str:
    """
    Full T-Cell security scan on ant output using the ImmuniSOC-Nexus engine.

    Classifies text into PUBLIC / STANDARD / CRITICAL tiers,
    assigns a ContainmentLevel (LOW → CRITICAL), and returns
    the full threat assessment with response actions.

    Params:
        ant_id: identifier of the ant that produced the text
        role:   ant role (scout / collector / queen)
        text:   the output text to scan
    """
    from immunisoc.tcell import process_ant_output, ContainmentLevel

    assessment = process_ant_output(ant_id=ant_id, role=role, text=text)

    lines = [
        f"🧬  T-Cell Assessment for {role}:{ant_id}",
        f"   Tier:              {assessment.tier.label()}",
        f"   Risk score:        {assessment.risk_score:.1f} / 10",
        f"   Containment:       {assessment.containment_level.label()}",
        f"   Threat type:       {assessment.threat_type}",
        f"   Quarantined:       {'YES ⛔' if assessment.quarantined else 'NO ✅'}",
    ]

    if assessment.findings:
        lines.append(f"   Findings ({len(assessment.findings)}):")
        for f_ in assessment.findings:
            lines.append(f"     • {f_}")

    if assessment.actions:
        lines.append(f"   Actions ({len(assessment.actions)}):")
        for a in assessment.actions:
            lines.append(f"     → {a.action_type} ({a.severity.label()}): {a.description}")

    return "\n".join(lines)


@tool
def honeytoken_check(ant_id: str, role: str, text: str) -> str:
    """
    Check if ant output contains honeytoken references (hallucination detector).

    Honeytokens are fake credentials injected into task context.
    If an ant's output references them, it means the ant hallucinated
    interacting with those credentials — a strong unreliability signal.

    Params:
        ant_id: identifier of the ant that produced the text
        role:   ant role
        text:   the output text to check
    """
    from immunisoc.deception import check_for_honeytokens

    detections = check_for_honeytokens(ant_id, role, text)
    if not detections:
        return "✅  No honeytoken references found — output appears genuine."

    lines = [f"🍯  HONEYTOKEN ALERT: {len(detections)} detection(s) for {role}:{ant_id}"]
    for d in detections:
        lines.append(f"   • Match type: {d['match']}")
        if "found" in d:
            lines.append(f"     Found: {d['found']}")
        if "token_id" in d:
            lines.append(f"     Token ID: {d['token_id']}")
    lines.append("   ⚠️  This output likely contains hallucinated credential usage.")
    return "\n".join(lines)


@tool
def validate_output(output: str) -> str:
    """
    Quality validation: checks output is complete, coherent, and safe.
    Params: output — the text to validate.
    """
    from ant_behavior import BehaviorParameters, protector_threat_decision
    from immunisoc.tcell import classify

    tier, risk_score, threat_type, findings = classify(output)
    params   = BehaviorParameters.from_heuristics()
    decision = protector_threat_decision(params, len(findings), risk_score)

    issues = list(findings)
    if len(output.strip()) < 20:
        issues.append("[quality] output too short")
    if "TODO" in output or "FIXME" in output:
        issues.append("[quality] unresolved placeholders")

    if not issues:
        verdict = "✅  Output validated — clean and complete."
    elif decision["should_quarantine"]:
        verdict = f"⛔  Output quarantined ({len(issues)} issue(s) exceed attack_power threshold)."
    else:
        verdict = f"⚠️  {len(issues)} issue(s) found — review recommended."

    lines = [verdict]
    for iss in issues:
        lines.append(f"  • {iss}")
    if decision["should_quarantine"]:
        lines.append(f"  Aggression level: {decision['aggression_level']:.2f}")

    return "\n".join(lines)
