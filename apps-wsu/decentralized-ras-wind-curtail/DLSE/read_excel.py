from xlrd import open_workbook

EXCEL_FILE = "H_matrix.xlsx"

def get_H_for_group(group_no):
        book = open_workbook(EXCEL_FILE)
        sheet = book.sheet_by_name("Group" + str(group_no))
        sheet_array = list()
        for row in sheet.get_rows():
                row_list = list()
                for x in row:
                        if x.ctype == 2:
                                row_list.append(x.value)
                        else:
                                row_list.append(None)
                sheet_array.append(row_list)
        return sheet_array

