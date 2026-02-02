from openpyxl import Workbook
from openpyxl.styles import Font
from datetime import datetime


def export_to_excel(headers, rows, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"

    # HEADER
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)

    # DATA
    for row_i, row in enumerate(rows, start=2):
        for col_i, value in enumerate(row, start=1):
            ws.cell(row=row_i, column=col_i, value=value)

    wb.save(filename)
