from docx import Document
import openpyxl

def xlsToString(file_obj):
    text = ""
    try:
        wb = openpyxl.load_workbook(file_obj, data_only=True)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            text += f"Sheet: {sheet_name}"
            merged_cells = sheet.merged_cells.ranges  # Get merged cell ranges
            for row in sheet.iter_rows():
                for cell in row:
                    if cell is not None and cell.value is not None:
                        text += str(cell.value)
                    else:
                        # Check if the cell is part of a merged cell range
                        for merged_range in merged_cells:
                            if cell is not None and sheet.cell(row=cell.row, column=cell.column).coordinate in merged_range:
                                # Get the value of the top-left cell of the merged range
                                top_left_cell = sheet.cell(row=merged_range.min_row, column=merged_range.min_col)
                                text += str(top_left_cell.value)
                                break
                text += "\n"
    except Exception as e:
        print("Error:", e)
    return text
print(xlsToString("D:\\Downloads\\2023032019000230803013.xlsx"))

