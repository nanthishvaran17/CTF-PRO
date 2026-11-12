import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

class ReportExporter:
    """Exports comprehensive CTF challenge intelligence to HTML, JSON, CSV, and PDF formats."""

    @classmethod
    def export_json(cls, challenge_data: Dict[str, Any], output_path: Path) -> Path:
        """Export as structured JSON."""
        output_path.write_text(json.dumps(challenge_data, indent=2), encoding="utf-8")
        return output_path

    @classmethod
    def export_csv(cls, challenge_data: Dict[str, Any], output_path: Path) -> Path:
        """Export candidate findings and evidence records as CSV."""
        candidates = challenge_data.get("candidates", [])
        fieldnames = [
            "flag", "status", "source_file", "source_sha256", "byte_offset",
            "extraction_method", "is_probable_decoy", "evidence_reasons"
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in candidates:
                reasons = "; ".join(c.get("evidence_reasons", [])) if isinstance(c.get("evidence_reasons"), list) else ""
                writer.writerow({
                    "flag": c.get("flag"),
                    "status": c.get("status"),
                    "source_file": c.get("source_file_name", ""),
                    "source_sha256": c.get("source_sha256", ""),
                    "byte_offset": c.get("byte_offset", ""),
                    "extraction_method": c.get("extraction_method", ""),
                    "is_probable_decoy": c.get("is_probable_decoy", False),
                    "evidence_reasons": reasons
                })
        return output_path

    @classmethod
    def export_html(cls, challenge_data: Dict[str, Any], output_path: Path) -> Path:
        """Generate interactive HTML report with cyberpunk theme and evidence links."""
        title = challenge_data.get("title", "CTF Challenge")
        category = challenge_data.get("category", "General")
        files = challenge_data.get("files", [])
        candidates = challenge_data.get("candidates", [])

        file_rows = "".join(f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #1E2740;"><code>{f.get('name')}</code></td>
                <td style="padding: 8px; border: 1px solid #1E2740;"><small>{f.get('sha256')}</small></td>
                <td style="padding: 8px; border: 1px solid #1E2740;">{f.get('file_type')}</td>
                <td style="padding: 8px; border: 1px solid #1E2740;">{f.get('size_bytes', 0):,} bytes</td>
                <td style="padding: 8px; border: 1px solid #1E2740;">{f.get('entropy', 0.0)}</td>
            </tr>
        """ for f in files)

        candidate_cards = "".join(f"""
            <div style="background: #121829; border: 1px solid #1E2740; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-family: monospace; font-size: 1.1rem; color: #22D3EE; font-weight: bold;">{c.get('flag')}</span>
                    <span style="padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; background: #1E2740; color: #A5F3FC;">{c.get('status')}</span>
                </div>
                <div style="margin-top: 8px; font-size: 0.85rem; color: #94A3B8;">
                    Source SHA-256: <code>{c.get('source_sha256', 'N/A')}</code> | Byte Offset: <code>{c.get('byte_offset', 'N/A')}</code> | Method: <code>{c.get('extraction_method')}</code>
                </div>
                <div style="margin-top: 6px; font-size: 0.85rem; color: #E2E8F0;">
                    <strong>Evidence Reasons:</strong> {", ".join(c.get('evidence_reasons', []))}
                </div>
            </div>
        """ for c in candidates) or "<p style='color: #64748B;'>No candidates discovered.</p>"

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CTF HUNTER X - Report: {title}</title>
    <style>
        body {{
            background-color: #0B0F1A;
            color: #F8FAFC;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 40px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #22D3EE; margin-bottom: 4px; }}
        .badge {{ background: #1E2740; color: #38BDF8; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: #121829; }}
        th {{ background: #162036; padding: 10px; text-align: left; border: 1px solid #1E2740; color: #94A3B8; font-size: 0.85rem; }}
        code {{ font-family: monospace; background: #1E2740; padding: 2px 6px; border-radius: 4px; color: #38BDF8; }}
        .limitations {{ background: #1A1829; border-left: 4px solid #A855F7; padding: 12px; margin-top: 24px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CTF HUNTER X Intelligence Report</h1>
        <p style="color: #94A3B8;">Challenge: <strong>{title}</strong> <span class="badge">{category}</span> | Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
        
        <h2>Target Files & Cryptographic Hashes</h2>
        <table>
            <thead>
                <tr><th>File</th><th>SHA-256</th><th>True Type</th><th>Size</th><th>Entropy</th></tr>
            </thead>
            <tbody>
                {file_rows}
            </tbody>
        </table>

        <h2 style="margin-top: 32px;">Flag Findings & Provenance</h2>
        {candidate_cards}

        <div class="limitations">
            <h3 style="margin-top: 0; color: #C084FC;">Limitations & Operational Bounds</h3>
            <ul style="margin-bottom: 0; font-size: 0.85rem; color: #CBD5E1;">
                <li>Original binary artifacts are treated as strictly immutable and read-only.</li>
                <li>Executable files were not run natively on host; analysis was performed via static header disassembly and string scanning.</li>
                <li>Flags marked <code>EVIDENCE-SUPPORTED</code> require final submission to the challenge scoreboard to reach <code>VERIFIED-BY-CHALLENGE</code>.</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        output_path.write_text(html_doc, encoding="utf-8")
        return output_path

    @classmethod
    def export_pdf(cls, challenge_data: Dict[str, Any], output_path: Path) -> Path:
        """Generate PDF report using ReportLab."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#0284C7"),
            spaceAfter=8
        )
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12)
        code_style = ParagraphStyle('CodeStyle', parent=styles['Code'], fontSize=8, leading=10, textColor=colors.HexColor("#0F172A"))

        # Header
        title = challenge_data.get("title", "CTF Challenge")
        story.append(Paragraph(f"CTF HUNTER X - Intelligence Report", title_style))
        story.append(Paragraph(f"<b>Challenge:</b> {title} | <b>Date:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", body_style))
        story.append(Spacer(1, 14))

        # Files Table
        files_data = [["Filename", "Type", "Size (bytes)", "SHA-256"]]
        for f in challenge_data.get("files", [])[:10]:
            files_data.append([
                f.get("name", "")[:20],
                f.get("file_type", "")[:10],
                f"{f.get('size_bytes', 0):,}",
                f.get("sha256", "")[:24] + "..."
            ])

        t_files = Table(files_data, colWidths=[120, 70, 80, 240])
        t_files.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_files)
        story.append(Spacer(1, 14))

        # Candidate Flags
        story.append(Paragraph("<b>Flag Candidates & Evidence:</b>", styles['Heading3']))
        candidates = challenge_data.get("candidates", [])
        if not candidates:
            story.append(Paragraph("No flag candidates discovered.", body_style))
        else:
            for c in candidates:
                story.append(Paragraph(f"<b>Flag:</b> {c.get('flag')} [{c.get('status')}]", body_style))
                story.append(Paragraph(f"Method: {c.get('extraction_method')} | Offset: {c.get('byte_offset')} | SHA: {c.get('source_sha256', '')[:16]}...", code_style))
                story.append(Spacer(1, 4))

        # Limitations Section
        story.append(Spacer(1, 14))
        story.append(Paragraph("<b>Honest Limitations & Environment Constraints:</b>", styles['Heading3']))
        story.append(Paragraph("All results reflect strictly deterministic analysis. No simulated or mock flags were generated.", body_style))

        doc.build(story)
        return output_path
