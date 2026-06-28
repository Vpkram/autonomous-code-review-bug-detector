import datetime
from fpdf import FPDF

# Generates markdown and PDF reports for a code review.
def generate_report(code: str, bugs: list, fixes: list) -> str:
    """
    Constructs a markdown code review report and creates a companion PDF report
    containing metadata, detected bugs, and code fixes.
    """
    try:
        # Date formatting
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Recommendation logic
        severities = [bug.get("severity", "").lower() for bug in bugs]
        if "high" in severities:
            recommendation = "CRITICAL"
        elif "medium" in severities:
            recommendation = "NEEDS FIX"
        else:
            recommendation = "PASS"

        # 1. Generate Markdown content
        md = []
        md.append("# Code Review Report")
        md.append(f"**Date/Time:** {date_str}\n")
        md.append("## Summary")
        md.append(f"- **Total Bugs Found:** {len(bugs)}")
        md.append(f"- **Total Fixes Generated:** {len(fixes)}")
        md.append(f"- **Final Recommendation:** {recommendation}\n")

        md.append("## Bug Table")
        md.append("| Line | Type | Severity | Description |")
        md.append("| --- | --- | --- | --- |")
        for bug in bugs:
            line = bug.get("line_number", "")
            b_type = bug.get("bug_type", "")
            sev = bug.get("severity", "")
            desc = bug.get("description", "")
            md.append(f"| {line} | {b_type} | {sev} | {desc} |")
        md.append("")

        md.append("## Fix Details")
        for idx, fix in enumerate(fixes):
            md.append(f"### Fix {idx + 1}")
            md.append("**Original Code:**")
            md.append("```python")
            md.append(code)
            md.append("```")
            md.append("**Evolved Fix:**")
            md.append("```python")
            md.append(fix)
            md.append("```\n")

        markdown_report = "\n".join(md)

        # 2. Generate PDF report
        try:
            pdf = FPDF()
            pdf.add_page()

            # Title
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "Code Review Report", ln=True, align="C")
            pdf.ln(5)

            # Date
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 10, f"Date: {date_str}", ln=True)
            pdf.ln(5)

            # Summary
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Summary", ln=True)
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 10, f"Total Bugs Found: {len(bugs)}", ln=True)
            pdf.cell(0, 10, f"Total Fixes Generated: {len(fixes)}", ln=True)
            pdf.cell(0, 10, f"Final Recommendation: {recommendation}", ln=True)
            pdf.ln(10)

            # Bug Table Title
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Bug Table", ln=True)
            pdf.ln(2)

            # Table Header
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(20, 10, "Line", border=1)
            pdf.cell(40, 10, "Type", border=1)
            pdf.cell(30, 10, "Severity", border=1)
            pdf.cell(100, 10, "Description", border=1)
            pdf.ln()

            # Table Data
            pdf.set_font("helvetica", "", 10)
            for bug in bugs:
                line = str(bug.get("line_number", ""))
                b_type = str(bug.get("bug_type", ""))
                sev = str(bug.get("severity", ""))
                desc = str(bug.get("description", ""))

                pdf.cell(20, 10, line, border=1)
                pdf.cell(40, 10, b_type, border=1)
                pdf.cell(30, 10, sev, border=1)
                pdf.cell(100, 10, desc[:50], border=1)
                pdf.ln()

            pdf.output("code_review_report.pdf")
            print("PDF: Successfully generated code_review_report.pdf")
        except Exception as pdf_err:
            print(f"PDF Error: Failed to generate report: {pdf_err}")

        return markdown_report

    except Exception:
        return "Report generation failed."
