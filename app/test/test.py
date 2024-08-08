from docx import Document
import openpyxl

from app.common.utils.file_utils import download_file, delete_file


def xlsToString(file_obj):
    result_text = ""
    try:
        wb = openpyxl.load_workbook(file_obj, data_only=True)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            result_text += f"Sheet: {sheet_name}"
            merged_cells = sheet.merged_cells.ranges  # Get merged cell ranges
            for row in sheet.iter_rows():
                text = ""
                for cell in row:
                    if cell is not None and cell.value is not None:
                        text = str(cell.value).replace("None", "").strip()
                        if text:
                            result_text += text + " "
                    else:
                        # Check if the cell is part of a merged cell range
                        for merged_range in merged_cells:
                            if cell is not None and sheet.cell(row=cell.row,
                                                               column=cell.column).coordinate in merged_range:
                                # Get the value of the top-left cell of the merged range
                                top_left_cell = sheet.cell(row=merged_range.min_row, column=merged_range.min_col)
                                text = str(top_left_cell.value).replace("None", "").strip()
                                if text:
                                    result_text += text + " "
                                break
                if text:
                    result_text += "\n"
    except Exception as e:
        print("Error:", e)
    return result_text.strip()


url = "http://xiaoxi-cdn.globeedu.com/2023/03/20/xlsx/2023032018555339603013.xlsx"

file_path = download_file(url, "downloads")
print(xlsToString(file_path))
# 删除临时文件
delete_file(file_path)
