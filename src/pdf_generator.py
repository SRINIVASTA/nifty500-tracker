from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class NiftyPDFGenerator:
    """Production ReportLab engine generating highly formatted accounting ledgers."""

    @staticmethod
    def generate(df: pd.DataFrame, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            rightMargin=20,
            leftMargin=20,
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
            spaceAfter=12,
        )
        cell_style = ParagraphStyle(
            "TableCell", parent=styles["Normal"], fontSize=7.5, leading=9
        )
        header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )

        elements = [
            Paragraph(
                "Nifty 500 Scrip Performance Executive Master Ledger",
                title_style,
            ),
            Spacer(1, 8),
        ]

        table_data = [[Paragraph(str(col), header_style) for col in df.columns]]

        for _, row in df.iterrows():
            row_data = []
            for col in df.columns:
                val = str(row[col])
                if col == "% Change":
                    val = f"{row[col]:+.2f}%"
                    color = (
                        "#00875A" if row["Direction"] == "Up" else "#DE350B"
                    )
                    c_style = ParagraphStyle(
                        "DeltaStyle",
                        parent=cell_style,
                        textColor=colors.HexColor(color),
                    )
                elif col == "Direction":
                    val = "🟢 Up" if row[col] == "Up" else "🔴 Down"
                    c_style = cell_style
                else:
                    c_style = cell_style

                row_data.append(Paragraph(val, c_style))
            table_data.append(row_data)

        # 7 Columns Form Factor Width Mapping (Fits landscape letter margins precisely)
        col_widths = [75, 180, 110, 100, 100, 65, 70]
        perf_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        perf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A2B4C")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F9FAFC")],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        elements.append(perf_table)
        doc.build(elements)
