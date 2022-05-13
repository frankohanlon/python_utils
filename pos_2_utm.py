#!/usr/bin/env python

import utm
import xlrd

main() :
    file_name = "/home/bob/Dropbox/uaf/2018 snow surveys/KG_Snow_Depth_V2_gisxlsx.xlsx"
    wb = xlrd.open_workbook(file_name)
    sheet = wb.sheet_by_index(0)
    n_rows = sheet.nrows
    n_cols = 2 #sheet.ncols
    o_val = [[],[]]
    for c_index in range(n_cols):
        for r_index in range(n_rows):
            try:
                temp = sheet.cell(r_index,c_index)

                if c_index == 0:
                    temp.value = datetime.datetime(*xlrd.xldate_as_tuple(temp.value,
                                                                wb.datemode))
                if c_index == 1:
                    # fail here if header type stuff or comments... drop to continue
                    temp.value = float(temp.value)
                o_val[c_index].append(temp.value)
            except:
                continue
    return o_val



if __name__ == "__main__":
    main()

