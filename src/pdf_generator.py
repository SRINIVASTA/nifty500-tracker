import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _register_unicode_fonts() -> tuple[str, str]:
    """Locate and register DejaVuSans on Linux (Streamlit Cloud) or Windows/Mac."""
    candidate_dirs = [
        "/usr/share/fonts/truetype/dejavu",           # Debian/Ubuntu (Streamlit Cloud)
        "/usr/share/fonts/dejavu",                    # Fedora/RHEL
        "C:/Windows/Fonts",                           # Windows fallback
        "/Library/Fonts",                             # macOS fallback
    ]

    for font_dir in candidate_dirs:
        regular_path = os.path.join(font_dir, "DejaVuSans.ttf")
        bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont("DejaVuSans", regular_path))
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_path))
            pdfmetrics.registerFontFamily(
                "DejaVuSans",
                normal="DejaVuSans",
                bold="DejaVuSans-Bold",
            )
            return "DejaVuSans", "DejaVuSans-Bold"

    return "Helvetica", "Helvetica-Bold"


REGULAR_FONT, BOLD_FONT = _register_unicode_fonts()


class NiftyPDFGenerator:
    """Production ReportLab engine generating highly formatted accounting ledgers."""

    @staticmethod
    def generate(df: pd.DataFrame, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=portrait(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName=BOLD_FONT,
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#1A2B4C"),
            spaceAfter=15,
        )
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName=REGULAR_FONT,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#333333"),
        )
        header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName=BOLD_FONT,
            fontSize=9,
            leading=12,
            textColor=colors.white,
        )

        elements = [
            Paragraph("Filtered Nifty 500 Market Performance Ledger", title_style),
            Spacer(1, 10),
        ]

        yesterday_col = [c for c in df.columns if "Close (" in c]
        yesterday_header = yesterday_col[-1] if yesterday_col else "Enddate Close Price"

        target_cols = ["NSE Ticker Symbol", "Company Name", yesterday_header, "Price Change", "Direction"]
        display_headers = ["NSE Ticker Symbol", "Company Name", "Enddate Close Price", "Price Change", "up/down"]

        table_data = [[Paragraph(h, header_style) for h in display_headers]]

        # Swap to "Rs." automatically if Unicode font wasn't found on the host
        currency_prefix = "₹" if REGULAR_FONT == "DejaVuSans" else "Rs. "

        for _, row in df.iterrows():
            row_data = []
            for original_col in target_cols:
                if original_col not in df.columns:
                    val = "N/A"
                    c_style = cell_style
                else:
                    val = str(row[original_col])
                    c_style = cell_style

                    if original_col == "Price Change":
                        try:
                            num_val = float(row[original_col])
                            val = f"{num_val:+.2f}"
                            val = val.replace("+", f"+{currency_prefix}").replace("-", f"-{currency_prefix}")
                        except ValueError:
                            pass
                        color = "#00875A" if row["Direction"] == "Up" else "#DE350B"
                        c_style = ParagraphStyle(
                            "DeltaColor", parent=cell_style, textColor=colors.HexColor(color), fontName=BOLD_FONT
                        )

                    elif original_col == "Direction":
                        val = "▲ Up" if row[original_col] == "Up" else "▼ Down"
                        color = "#00875A" if row[original_col] == "Up" else "#DE350B"
                        c_style = ParagraphStyle(
                            "DirColor", parent=cell_style, textColor=colors.HexColor(color), fontName=BOLD_FONT
                        )

                    elif "Close" in original_col or "₹" in original_col:
                        try:
                            val = f"{currency_prefix}{float(row[original_col]):,.2f}"
                        except ValueError:
                            pass

                row_data.append(Paragraph(val, c_style))
            table_data.append(row_data)

        # Exact grid width mapping matching Portrait bounds (Summing to 552 points)
        col_widths = [90, 175, 120, 97, 70]

        perf_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        perf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A2B4C")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elements.append(perf_table)
        doc.build(elements)
