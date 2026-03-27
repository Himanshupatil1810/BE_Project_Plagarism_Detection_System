# services/report_export_service.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


class ReportExportService:

    def wrap_text(self, text, max_chars):
        """Utility to wrap long text"""
        words = text.split()
        lines = []
        line = ""

        for word in words:
            if len(line + word) < max_chars:
                line += word + " "
            else:
                lines.append(line)
                line = word + " "

        lines.append(line)
        return lines


    def draw_progress_bar(self, c, x, y, width, height, percent, color):
        """Draw horizontal progress bar"""
        c.setStrokeColor(colors.lightgrey)
        c.rect(x, y, width, height, stroke=1, fill=0)

        fill_width = width * (percent / 100)
        c.setFillColor(color)
        c.rect(x, y, fill_width, height, stroke=0, fill=1)


    def generate_pdf_report(self, report_data, output_path):
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        metadata = report_data.get('metadata', {}) or {}
        stats = metadata.get('document_stats', {})
        sections = metadata.get('plagiarized_sections', [])

        # Clean BOM
        for sec in sections:
            if 'text' in sec:
                sec['text'] = sec['text'].replace('\ufeff', '')

        # Scores
        raw_score = report_data.get('overall_score', 0)
        plagiarism = round(float(raw_score) * 100) if float(raw_score) <= 1 else round(float(raw_score))
        unique = 100 - plagiarism

        # ================= HEADER =================
        c.setFont("Helvetica-Bold", 20)
        c.drawString(40, height - 50, "Plagiarism Scan Report")

        # ================= SUMMARY CARD =================
        c.setStrokeColor(colors.lightgrey)
        c.roundRect(40, height - 200, 520, 120, 12, stroke=1)

        # --- Plagiarism ---
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.red)
        c.drawString(60, height - 100, f"{plagiarism}% Plagiarism")

        self.draw_progress_bar(c, 60, height - 115, 200, 10, plagiarism, colors.red)

        # --- Unique ---
        c.setFillColor(colors.green)
        c.drawString(60, height - 140, f"{unique}% Unique")

        self.draw_progress_bar(c, 60, height - 155, 200, 10, unique, colors.green)

        # --- STATS BOX ---
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)

        c.drawString(320, height - 95, f"Words: {stats.get('word_count', 'N/A')}")
        c.drawString(320, height - 110, f"Characters: {stats.get('character_count', 'N/A')}")
        c.drawString(320, height - 125, f"Sentences: {stats.get('sentence_count', 'N/A')}")
        c.drawString(320, height - 140, f"Reading Level: {stats.get('reading_level', 'N/A')}")

        # Divider
        c.setStrokeColor(colors.grey)
        c.line(40, height - 210, 560, height - 210)

        # ================= CONTENT TITLE =================
        y = height - 240
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Content Checked For Plagiarism")
        y -= 20

        # ================= SECTIONS =================
        for sec in sections:

            if y < 100:
                c.showPage()
                y = height - 50

            txt = sec.get('text', '')
            risk = sec.get('risk', 'High')

            # Risk color
            if risk == "High":
                color = colors.red
            elif risk == "Medium":
                color = colors.orange
            else:
                color = colors.green

            # Wrap text
            wrapped_lines = self.wrap_text(txt, 90)

            box_height = 20 + (len(wrapped_lines) * 12)

            # Card
            c.setStrokeColor(colors.lightgrey)
            c.roundRect(40, y - box_height, 520, box_height, 8, stroke=1)

            # Risk badge
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y - 15, risk.upper())

            # Text
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)

            text_y = y - 15
            for line in wrapped_lines[:4]:  # limit lines
                c.drawString(110, text_y, line)
                text_y -= 12

            y -= (box_height + 10)

        c.save()