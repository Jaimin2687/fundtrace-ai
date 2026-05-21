"""
fundtrace-worker: Compliance & Audit Worker (mock implementation).
Heavy IO tasks executed outside the API event loop.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_fiu_str_report(case_id: str) -> Tuple[str, str]:
    """
    Generate a mock FIU-IND report PDF and return (path, url).
    """
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / f"fiu-ind-{case_id}.pdf"

    buffer = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4
    buffer.setFont("Helvetica-Bold", 16)
    buffer.drawString(40, height - 60, "FundTrace AI - FIU-IND Draft Report")
    buffer.setFont("Helvetica", 10)
    buffer.drawString(40, height - 80, f"Case ID: {case_id}")
    buffer.drawString(40, height - 95, f"Generated: {datetime.now(timezone.utc).isoformat()}")
    buffer.save()

    return str(file_path), f"/downloads/{file_path.name}"


def recalculate_peer_baselines() -> str:
    """
    Mock nightly batch job to update peer baselines.
    """
    return "baseline job queued"
