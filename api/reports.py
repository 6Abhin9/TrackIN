import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from django.http import HttpResponse

def report_as_excel(title, header, admission_data, file_name, mode):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title

    headers = header

    # Merging cells for title
    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=len(headers))
    title_cell = ws.cell(row=1, column=1)
    title_cell.value = title
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    title_cell.fill = PatternFill(fill_type='solid', fgColor='FFFFFF')
    title_cell.border = Border(
        left=Side(border_style='thin'), 
        right=Side(border_style='thin'), 
        top=Side(border_style='thin'), 
        bottom=Side(border_style='thin')
    )

    # Apply column header styling
    for col_num, (column_title, column_width) in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_num)
        cell.value = column_title
        cell.font = Font(bold=True, color='FFFFFF')
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = column_width
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.fill = PatternFill(fill_type='solid', fgColor='01307A')
        cell.border = Border(
            left=Side(border_style='thin'), 
            right=Side(border_style='thin'), 
            top=Side(border_style='thin'), 
            bottom=Side(border_style='thin')
        )

    # Populate the data rows
    for row_num, key in enumerate(admission_data, start=4):
        if mode == 1:
            row_data = [
                row_num - 3,
                admission_data[key]['License_id'],
                admission_data[key]['course_name'],
                admission_data[key]['total_students'],
             
            ]

            for col_num, cell_value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = cell_value
                cell.alignment = Alignment(vertical='center')
                cell.border = Border(
                    left=Side(border_style='thin'), 
                    right=Side(border_style='thin'), 
                    top=Side(border_style='thin'), 
                    bottom=Side(border_style='thin')
                )

    # Save the workbook to the response
    wb.save(response)
    return response
