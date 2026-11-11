import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

class NiftyPDFGenerator:
    """Production ReportLab engine generating highly formatted accounting ledgers."""

    @staticmethod
    def generate(df: pd.DataFrame, output_path: str):
        # portrait form factor cleanly housing 5 high-precision tracking columns
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
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1A2B4C"),
            spaceAfter=15,
        )
        cell_style = ParagraphStyle(
            "TableCell", parent=styles["Normal"], fontSize=9, leading=11, textColor=colors.HexColor("#333333")
        )
        header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=12,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )

        elements = [
            Paragraph("Filtered Nifty 500 Market Performance Ledger", title_style),
            Spacer(1, 10),
        ]

        # Isolate target trailing data engine header
        yesterday_col = [c for c in df.columns if "Close (" in c]
        yesterday_header = yesterday_col[-1] if yesterday_col else "Enddate Close Price"

        # Map structural array values to your exact 5 columns schema
        target_cols = ["NSE Ticker Symbol", "Company Name", yesterday_header, "Price Change", "Direction"]
        display_headers = ["NSE Ticker Symbol", "Company Name", "Enddate Close Price", "Price Change", "up/down"]
        
        table_data = [[Paragraph(h, header_style) for h in display_headers]]

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
                            val = val.replace("+", "+₹").replace("-", "-₹")
                        except ValueError:
                            pass
                        color = "#00875A" if row["Direction"] == "Up" else "#DE350B"
                        c_style = ParagraphStyle("DeltaColor", parent=cell_style, textColor=colors.HexColor(color), fontName="Helvetica-Bold")
                    
                    elif original_col == "Direction":
                        val = "▲ Up" if row[original_col] == "Up" else "▼ Down"
                        color = "#00875A" if row[original_col] == "Up" else "#DE350B"
                        c_style = ParagraphStyle("DirColor", parent=cell_style, textColor=colors.HexColor(color), fontName="Helvetica-Bold")
                        
                    elif "Close" in original_col or "₹" in original_col:
                        try:
                            val = f"₹{float(row[original_col]):,.2f}"
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
