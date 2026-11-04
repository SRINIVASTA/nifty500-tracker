import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

class NiftyPDFGenerator:
    """Production ReportLab engine generating highly formatted accounting ledgers."""

    @staticmethod
    def generate(df: pd.DataFrame, output_path: str):
        # Establish landscape-letter bounds with tight document margins to handle 500 rows elegantly across page overflows
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            rightMargin=25,
            leftMargin=25,
            topMargin=30,
            bottomMargin=30,
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
            "TableCell", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#333333")
        )
        header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )

        elements = [
            Paragraph("Alphabetical Nifty 500 Scrip Performance Master Tracker", title_style),
            Spacer(1, 5),
        ]

        # Explicitly read out columns in the order mapped on the desktop screen view
        cols = list(df.columns)
        table_data = [[Paragraph(str(col), header_style) for col in cols]]

        for _, row in df.iterrows():
            row_data = []
            for col in cols:
                val = str(row[col])
                c_style = cell_style
                
                # Apply high-precision formatting changes dynamically to column values
                if col == "% Change":
                    try:
                        num_val = float(row[col])
                        val = f"{num_val:+.2f}%"
                    except ValueError:
                        pass
                    color = "#00875A" if row["Direction"] == "Up" else "#DE350B"
                    c_style = ParagraphStyle("DeltaColor", parent=cell_style, textColor=colors.HexColor(color), fontName="Helvetica-Bold")
                
                elif col == "Direction":
                    val = "■ Up" if row[col] == "Up" else "■ Down"
                    color = "#00875A" if row[col] == "Up" else "#DE350B"
                    c_style = ParagraphStyle("DirColor", parent=cell_style, textColor=colors.HexColor(color))
                    
                elif isinstance(row[col], (int, float)) and "Close" in col:
                    val = f"{float(row[col]):.2f}"

                row_data.append(Paragraph(val, c_style))
            table_data.append(row_data)

        # 7-Column Form Factor Grid Width Mapping (Exactly fits landscape parameters)
        # Sequence layout: Ticker, Company Name, Industry, Prev Close, Curr Close, % Change, Direction
        col_widths = [85, 180, 140, 95, 95, 75, 70]
        
        perf_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        perf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A2B4C")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        elements.append(perf_table)
        doc.build(elements)
