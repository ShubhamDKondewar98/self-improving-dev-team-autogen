from fpdf import FPDF


def generate_pdf_report(run_result: dict, output_path: str = "run_report.pdf") -> str:
    """
    Generates a simple PDF report from a run's result dict.
    NOTE: uses fpdf2 -- run `uv add fpdf2` first.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Dev Team Run Report", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, f"Task: {run_result.get('task', '')}")
    pdf.multi_cell(0, 8, f"Stop reason: {run_result.get('stop_reason', '')}")
    pdf.multi_cell(0, 8, f"Final verdict: {run_result.get('final_verdict', '')}")
    pdf.multi_cell(0, 8, f"Failure category: {run_result.get('failure_category', 'None')}")
    pdf.multi_cell(0, 8, f"Code retries: {run_result.get('code_retry_count', 0)}")
    pdf.multi_cell(0, 8, f"Test retries: {run_result.get('test_retry_count', 0)}")

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Critic Reasoning", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, run_result.get("critic_reasoning") or "N/A")

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Final Code", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 9)
    pdf.multi_cell(0, 5, run_result.get("final_code") or "No code produced.")

    pdf.output(output_path)
    return output_path