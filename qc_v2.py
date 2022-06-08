
#!/usr/bin/python3
"""
Updating of the old qc.py hopefully for a big speed boost and reduction execution time.

Going to borrow quite a bit from recently updated glom3.py

I guess sitting here thinking I should file away to handle xls / xlsx / ods independently.

 python3 qc_v2.py -i /Users/elle/hooptydata/uaf_sp/teller_bottom/outputs/summer_rain_Tot.csv -c /Users/elle/hooptydata/uaf_sp/teller_bottom/qc/teller_bottom_fix_rain_2019.xlsx

 python3 qc_v2.py -i /Users/elle/hooptydata/uaf_sp/teller_bottom/outputs/ws_374cm_Wvc.csv -c /Users/elle/hooptydata/uaf_sp/teller_bottom/qc/teller_bottom_fix_WIND.xls


"""
# of the items on this list, pyexcel_ods3 and arrow are not python default install items.

# pip3 install arrow
#pip3 install pyexcel
#pip3 install pandas
#pip3 install pyexcel-xls
#pip3 install pyexcel-xlsx
#pip3 install pyexcel-ods3

import arrow
import pyexcel
import pandas
import os
import argparse
import sys


class source_spreadsheet () :
    """
    Class specifically for reading in a variety of spreadsheets:
    libre office ods
    excel xls
    excel xlsx

    Once they're loaded up then dump the data into a list that can be used for other purposes.

    """
    #import openpyxl
    import pyexcel
    import pathlib

    import arrow
    input_spreadsheet = ''
    sheet_combined_list = []
    sheet_date_list = []
    sheet_numbers_list = []
    spreadsheet_filetype = ''

    def set_prop(self, parameter, value):
        """
        Short and quick property setter to set up the station info
        :param parameter: This is the general parameter from the yaml.  e.g. 'StationName'
        :param value: This is the string or boolean value itself.


        :return:
        """
        if parameter == 'corrections_spreadsheet' :
            self.input_spreadsheet = value
            self.spreadsheet_filetype = self.input_spreadsheet.split('.')[-1]
            # could read in the header here but I think it makes sense to wait.

    def read_in_spreadsheet_data_file(self):
        """
        Load the manual quality corrections here.

        :return:
        """
        self.sheet_date_list = []  # this will be a list of arrow objects
        self.sheet_numbers_list = []  # this will hold the data.
        self.sheet_combined_list = []  # thinking for concatenation subselections maybe this will be faster.

        print('reading in spreadsheet')
        # open the spreadsheet file:
        print(self.input_spreadsheet)
        if self.spreadsheet_filetype  == 'xls' :
            print('Unfortunately .xls no longer supported by primary library.\n\n  Please save spreadsheet as .xlsx format Excel or .ods format from LibreOffice\n\n')
        # open spreadsheet
        wb = pyexcel.get_sheet(file_name= self.input_spreadsheet)


        for row in wb.row: #[:20] :
            try:
                # check if column A contains a datetime
                # if row[0] is not a date we get booted here:
                # temp_date isn't used for anything else.
                temp_date = arrow.get(row[0], tzinfo='Etc/GMT+0')

                date_string = str(row[0]) # had some shenanigans with timezones and decimal dates using datetimes
                temp_value = str(row[1])
                temp_log = row[2]

                # now I have loaded a row.
                #self.sheet_date_list.append(temp_date)
                # Need to do a bit more work
                # One ugly bit, the number to date conversion in the spreadsheet seems to be doing a lot of
                # 10:59 for time instead of 11:00 once I switched from xls to ods.
                # probably could adjust further
                # could use arrow but asterisk the dates are converted to localtime with arrow (utc-8 or -9)
                # so it's possible it isn't quite as easy as it seems.
                if len(date_string) == 19 :
                    date_string = '"' + date_string[:-2] + '00"'
                elif len(date_string) == 26:
                    date_string = '"' + date_string[:-9] + '00"'
                elif len(date_string) == 10 :
                    date_string = '"' + date_string + ' 00:00:00"'
                line_string = date_string + ',' + temp_value
                self.sheet_numbers_list.append(temp_value)
                self.sheet_date_list.append(date_string)
                self.sheet_combined_list.append(line_string)
            except:
                if row[0] != '' and row[0] != 'break':
                    # Column A is not a date but a comment.
                    print('non date line', row[:])

                pass
        self.sheet_date_list.sort()
        self.sheet_combined_list.sort()

class input_timeseries () :
    """
    This is not that great of a name.  The gist here is this will be filled with
    paramters from one input csv
    and it's possible this class can be reused for the manual qa program revision.
    """
    input_csv  = ''                 # key piece of the puzzle, absolute path to the input csv.
    output_file_path = ''           # absolute path to where output csv will end up.
    output_filename_root = ''       # this should be like the root of the name with '_YYYY.csv'
                                    # or _ddd.csv appended by this program.
    output_format_csi = False       #  Either pandas format or csi format (1 line header vs 4 line)
    alt_header_title = ''           # for mixed combined csvs the header from the original might be
                                    # generic like 'Air Temp 1.85m'
                                    # preferred may be 'Teller Bottom Air Temp'
                                    # to pair with 'Teller Top Air Temp'
    input_csv_format_csi = True     # similar to output format.  True = 4line header, False = 1 line header
    input_csv_header_line_1 = 'TOA5'    # CampbellSci format data has four header lines
    input_csv_header_line_2 = 'TIMESTAMP'    # CampbellSci format data has four header lines (& pandas just 1)
    input_csv_header_line_3 = 'TS'    # CampbellSci format data has four header lines (& pandas just 1)
    input_csv_header_line_4 = ''    # CampbellSci format data has four header lines (& pandas just 1)
    input_csv_full_line_1 = ''      # used for qc program which recreates the original file plus the corrected data.
    input_csv_full_line_2 = ''      # used for qc program which recreates the original file plus the corrected data.
    input_csv_full_line_3 = ''      # used for qc program which recreates the original file plus the corrected data.
    input_csv_full_line_4 = ''      # used for qc program which recreates the original file plus the corrected data.
    csv_date_list=[]                # this will be a list of arrow objects
    csv_numbers_list = []           # this will hold the data.
    csv_combined_list = []          # thinking for concatenation subselections maybe this will be faster.
    csv_subset_list = []
    csv_start_date = ''             # needed for creating the pandas data frames.
    csv_end_date = ''               # needed for creating the pandas data frames.
    start_year = 2000
    end_year = 2001
    csv_time_interval = ''          # also needed.
    csv_date_series = pandas.Series(dtype='datetime64[ns]')
    csv_data_series = pandas.Series(dtype='float64')
    csv_df = pandas.DataFrame()

    def set_prop(self, parameter, value):
        """
        Short and quick property setter to set up the station info
        :param parameter: This is the general parameter from the yaml.  e.g. 'StationName'
        :param value: This is the string or boolean value itself.


        :return:
        """
        if parameter == 'input_csv' :
            self.input_csv = value
            # could read in the header here but I think it makes sense to wait.
        elif parameter == 'alt_header_title' :
            self.alt_header_title = value
        elif parameter == 'input_csv_format_csi' :
            self.input_csv_format_csi = parameter

    def read_in_data_file_combined(self):
        """
        Once the yaml has been fully read in, fire off this function to load the csv data.

        THe wrinkle with this one, leave the lines as-is and don't split them out until the years have been selected
        on a later step.
        :return:
        """
        self.csv_date_list = []  # this will be a list of arrow objects
        self.csv_numbers_list = []  # this will hold the data.
        self.csv_combined_list = []  # thinking for concatenation subselections maybe this will be faster.

        dfile = open(self.input_csv)
        csv_lines = dfile.readlines()
        dfile.close()
        row_num = 0
        full_date_list = []
        # hop through the lines... we don't care how big the header is here
        # or whether it is pandas format or csi format date value
        for row in csv_lines[:]:
            row_num += 1
            temp = row.rstrip()
            row_list = temp.split(',')
            if self.input_csv_format_csi == True :  # This is the T0A5 format
                if row_num == 1:
                    self.input_csv_header_line_1 = row_list[1]
                    self.input_csv_full_line_1 = temp
                elif row_num == 2:
                    if self.alt_header_title == '' :
                        # alt_header_title is used for output.
                        # so, if the default from original file is preferred, set that value here.
                        self.alt_header_title = row_list[1]
                    self.input_csv_full_line_2 = temp
                    self.input_csv_header_line_2 = row_list[1]
                elif row_num == 3:
                    self.input_csv_header_line_3 = row_list[1]
                    self.input_csv_full_line_3 = temp
                elif row_num == 4:
                    self.input_csv_header_line_4 = row_list[1]
                    self.input_csv_full_line_4 = temp
            else: # pandas formatted csv
                if row_num == 1:
                    if self.alt_header_title == '' :
                        # alt_header_title is used for output.
                        # so, if the default from original file is preferred, set that value here.
                        self.alt_header_title = row_list[1]
            # now onward, to the data.
            if len(row_list) == 2:
                # here is a bit of weirdness but sometimes the csvs come sans double quotes and sometimes they arrive with.
                # so do a check here first and then make sure they exit fully quoted... for the qc program
                date_temp = row_list[0].lstrip('"').rstrip('"')

                try:
                    # .naive at the end finishes the date as a datetime.
                    # pandas can't currently handle arrow objects.
                    # https://github.com/pandas-dev/pandas/issues/27817
                    temp_date = arrow.get(date_temp, 'YYYY-MM-DD HH:mm:ss', tzinfo='Etc/GMT+0')
                    cur_date = temp_date.strftime('"%Y-%m-%d %H:%M:%S"')
                    if abs(float(row_list[1])) == 6999. :
                        value_temp = '6999.'
                    else:
                        value_temp = row_list[1]
                    # if we've made it this far then the row_list[0] is a date.
                    full_date_str = '"' + date_temp + '"'
                    line_string = ','.join([full_date_str, value_temp])
                    full_date_list.append(cur_date)
                    self.csv_date_list.append(cur_date)
                    self.csv_combined_list.append(line_string)

                except:
                    # with a print() here this seems to be just catching csv header rows.
                    pass
        # needed for setting things up later:
        self.csv_start_date = full_date_list[0]
        self.csv_end_date = full_date_list[-1]
        #self.start_year = int(full_date_list[0].strftime('%Y') )
        #self.end_year = int(full_date_list[-1].strftime('%Y') )  +1
        # also compute interval here... and I suppose use self.csv_date_list[-1] and self.csv_date_list[-2]
        # these are needed for doing the last X days type output.
        #diff = arrow.get(full_date_list[-1]) - arrow.get(full_date_list[-2])
        #(junk_day, second_interval)  = divmod(diff.total_seconds(), 86400)
        #self.csv_time_interval = 86400 / second_interval


def main() :
    """
    No returns, just where the magic happens.
    :return:
    """
    parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input_csv', type=str, required=True,
                        help="Full filename and path for the input file csv ")
    parser.add_argument('-c', '--corrections_spreadsheet', type=str, required=True,
                        help="Full file name and path for the input spreadsheet")

    # Read in the command line parameters
    args = parser.parse_args()


    if args.input_csv != None:
        # verify the input csv exists before continuing.
        input_csv = args.input_csv
        if os.path.exists(input_csv) == False :
            print('Sorry recheck your command line.  This file not found: ', input_csv)
            sys.exit()
    if args.corrections_spreadsheet != None:
        # confirm the correction spreadsheet also exists
        corrections_spreadsheet = args.corrections_spreadsheet
        if os.path.exists(corrections_spreadsheet) == False:
            print('Sorry recheck your command line.  This file not found: ', corrections_spreadsheet)
            sys.exit()

    source_csv = input_timeseries()
    source_csv.set_prop('input_csv', input_csv)
    source_csv.read_in_data_file_combined()
    qc_spreadsheet = source_spreadsheet()
    qc_spreadsheet.set_prop('corrections_spreadsheet', corrections_spreadsheet)
    qc_spreadsheet.read_in_spreadsheet_data_file()

    for sample in qc_spreadsheet.sheet_date_list:#[:5]:
        # check to see if the date is in the full data set(it should be)
        #print(type(sample), sample)
        #print(type(source_csv.csv_date_list[3]), source_csv.csv_date_list[-7003])
        if sample in source_csv.csv_date_list :
            # If it is, then proceed with swap.
            source_index = source_csv.csv_date_list.index(sample)
            qc_index = qc_spreadsheet.sheet_date_list.index(sample)
            #print(sample, '  ',qc_index,  qc_spreadsheet.sheet_combined_list[qc_index], '  ', source_index, '  ', source_csv.csv_combined_list[source_index])
            source_csv.csv_combined_list[source_index]= qc_spreadsheet.sheet_combined_list[qc_index]
        else:
            print(sample, '  not found  ')
    # at this point we've run through the full file.  time to save to csv again.
    out_csv_list = [source_csv.input_csv_full_line_1, source_csv.input_csv_full_line_2, source_csv.input_csv_full_line_3, source_csv.input_csv_full_line_4]
    for row in source_csv.csv_combined_list :
        out_csv_list.append(row)
    out_csv_text = '\n'.join(out_csv_list)
    out_csv_text += '\n'
    fh = open(source_csv.input_csv, 'w')
    fh.write(out_csv_text)
    fh.close()

if __name__ == '__main__':
  main()
