#!/usr/bin/python3
"""
Updating of the old glom2gether.py hopefully to make it easier to use on the fly.

"""
# of the items on this list, yaml and arrow are not python default install items.
# pip3 install pyyaml
# pip3 install arrow
import yaml
import arrow
import os
import argparse
import sys
import pandas
import numpy
import copy

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
        try:
            dfile = open(self.input_csv)
        except:
            print('File Not Found:  ', self.input_csv)
            sys.exit()
        csv_lines = dfile.readlines()
        dfile.close()
        row_num = 0
        full_date_list = []
        # hop through the lines... we don't care how big the header is here
        # or whether it is pandas format or csi format date value
        for row in csv_lines:
            row_num += 1
            temp = row.rstrip()
            row_list = temp.split(',')
            if self.input_csv_format_csi == True :  # This is the T0A5 format
                if row_num == 1:
                    self.input_csv_header_line_1 = row_list[1]
                elif row_num == 2:
                    if self.alt_header_title == '' :
                        # alt_header_title is used for output.
                        # so, if the default from original file is preferred, set that value here.
                        self.alt_header_title = row_list[1]
                    self.input_csv_header_line_2 = row_list[1]
                elif row_num == 3:
                    self.input_csv_header_line_3 = row_list[1]
                elif row_num == 4:
                    self.input_csv_header_line_4 = row_list[1]
            else: # pandas formatted csv
                if row_num == 1:
                    if self.alt_header_title == '' :
                        # alt_header_title is used for output.
                        # so, if the default from original file is preferred, set that value here.
                        self.alt_header_title = row_list[1]
            # now onward, to the data.
            if len(row_list) == 2:
                date_temp = row_list[0].lstrip('"').rstrip('"')
                process= True
                try:
                    # .naive at the end finishes the date as a datetime.
                    # pandas can't currently handle arrow objects.
                    # https://github.com/pandas-dev/pandas/issues/27817
                    cur_date = arrow.get(date_temp, 'YYYY-MM-DD HH:mm:ss').naive
                except:
                    process=False
                if process==True:
                    if abs(float(row_list[1])) == 6999. :
                        value_temp = '6999.0' #'NaN'
                    else:
                        value_temp = row_list[1]
                    line_string = ','.join([date_temp, value_temp])
                    full_date_list.append(cur_date)
                    self.csv_combined_list.append(line_string)
                #except:
                #    pass
        # needed for setting things up later:
        self.csv_start_date = full_date_list[0]
        self.csv_end_date = full_date_list[-1]
        self.start_year = int(full_date_list[0].strftime('%Y') )
        self.end_year = int(full_date_list[-1].strftime('%Y') )  +1
        # also compute interval here... and I suppose use self.csv_date_list[-1] and self.csv_date_list[-2]
        # these are needed for doing the last X days type output.
        diff = arrow.get(full_date_list[-1]) - arrow.get(full_date_list[-2])
        # currently fails for daily data...
        (junk_day, second_interval)  = divmod(diff.total_seconds(), 86400)
        self.csv_time_interval = 86400 / second_interval

    def convert_2_pandas(self):
        """
        For the interval probably can add a function to compute and / or compute at csv read in.
        set up the pandas data frame for later use
        :return:
        """
        # one thing to note here, need to convert 6999s to nans.  that hasn't been done yet.
        temp_df = pandas.DataFrame(data=self.csv_subset_list,
                                       columns=['Date', self.alt_header_title])

        temp_df = temp_df.set_index('Date')
        self.csv_df = copy.deepcopy(temp_df)


    def subset_year(self, year):
        """
        Pull year values
        :param year:
        :return:
        """
        self.csv_subset_list = []
        matches = []
        local_csv_subset_list = []
        for match in self.csv_combined_list:
            if year in match:
                matches.append(match)
        matches.sort()

        for row in matches:
            temp = row.rstrip()
            row_list = temp.split(',')
            date_temp = row_list[0].lstrip('"').rstrip('"')
            cur_date = arrow.get(date_temp, 'YYYY-MM-DD HH:mm:ss').naive
            value_temp = float(row_list[1])
            local_csv_subset_list.append([cur_date, value_temp])
        self.csv_subset_list = copy.deepcopy(local_csv_subset_list)

    def subset_tail(self, tail):
        """
        Pull the last X number of days.
        :param year:
        :return:
        """
        ending_tail = - abs(tail)
        self.csv_subset_list = []
        local_csv_subset_list = []
        matches = self.csv_combined_list[ending_tail:]
        matches.sort()

        for row in matches:
            temp = row.rstrip()
            row_list = temp.split(',')
            date_temp = row_list[0].lstrip('"').rstrip('"')
            cur_date = arrow.get(date_temp, 'YYYY-MM-DD HH:mm:ss').naive
            value_temp = float(row_list[1])
            local_csv_subset_list.append([cur_date, value_temp])
        self.csv_subset_list = copy.deepcopy(local_csv_subset_list)

def main() :
    """
    No returns, just where the magic happens.
    :return:
    """
    parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-g', '--grouper_yaml', type=str, required=True,
                        help="Yaml that contains proper fields to fill the grouper")
    parser.add_argument('-y', '--output_year', type=int, required=False,
                        help="generate a year file where the year is specified here.  Choose this flag or -d")
    parser.add_argument('-d', '--output_days', type=int, required=False,
                        help="generate a last X number of days file.  Choose this flag or -y")
    parser.add_argument('-a', '--output_all_years', action='store_true', required=False,
                        help="generate a year file for each year in first csv.  Choose this flag or -d")

    # Read in the command line parameters
    args = parser.parse_args()
    G_YAML = args.grouper_yaml

    save_year = False
    output_all_years = False
    days = -2
    save_tail = False
    if args.output_year != None:
        try:
            print('Year value: ', args.output_year)
            start_year = args.output_year
            end_year =  args.output_year+1
            save_year = True
        except:
            print('Sorry, not a legit year value')
            sys.exit()
    if args.output_days != None:
        try:
            print('Days Value: ', args.output_days)
            days = args.output_days
            save_tail = True
        except:
            print('Sorry, not a legit days value')
            sys.exit()
    if args.output_days != None and args.output_year != None :
        print('Choose to output a year or a last number of days but not both ')
        sys.exit()
    elif args.output_days == None and args.output_year == None and args.output_all_years == False:
        print('Need to use -d option to select # of days to output or -y to output a specific year.')
        sys.exit()
    elif args.output_all_years == True:
        output_all_years = True
        save_year = True
    # open the yaml file
    try:
        with open(G_YAML, 'rt') as file :
            glom_full = yaml.safe_load(file)
    except:
        print("Problem finding YAML: ", Diag_YAML)
        sys.exit()

    # what I would like to do here is:
    # open the csvs
    # grab the header info
    # optionally replace the header info
    # make sure everything is a pandas format
    # output by specified year / all years or last X days
    output_file_path = glom_full['output_file_path']
    output_filename_root = glom_full['output_filename_root']
    try:
        output_format_csi = glom_full['output_format_csi']
    except:
        output_format_csi = False
    first_station = glom_full['data_files'][0]
    station_object = input_timeseries()
    station_object.set_prop('input_csv', first_station['input_csv'])
    station_object.read_in_data_file_combined()
    if output_all_years == True:
        start_year = station_object.start_year
        end_year = station_object.end_year
    if save_tail == True:
        readings_per_day = station_object.csv_time_interval
        rows_to_tail = int(readings_per_day * days)
    del station_object
    if save_year == True:
        for year in range(start_year, end_year) :
            df_for_concat = []
            if output_format_csi == True:
                header_line1 = ['TOA5','']
                header_line2 = ['TIMESTAMP']
                header_line3 = ['TS']
                header_line4 = ['']
            for station in glom_full['data_files']:
                station_object = input_timeseries()
                station_object.set_prop('input_csv', station['input_csv'])
                station_object.set_prop('alt_header_title', station['alt_header_title'])
                station_object.read_in_data_file_combined()
                station_object.subset_year(str(year))
                station_object.convert_2_pandas()
                df_for_concat.append(station_object.csv_df)
                if output_format_csi == True :
                    header_line2.append(station_object.input_csv_header_line_2)
                    header_line3.append(station_object.input_csv_header_line_3)
                    header_line4.append(station_object.input_csv_header_line_4)
            # ok, files are read in...
            # now, group and save to file again.
            df_stuff = pandas.concat(df_for_concat, axis=1)

            # file saving...
            full_file_output_name = output_file_path + output_filename_root + '_' + str(year) + '.csv'
            if output_format_csi == False :
                df_stuff.to_csv(full_file_output_name)
            else:
                # do a bit more work to make the header
                full_header = [ ','.join(header_line1), ','.join(header_line2), ','.join(header_line3), ','.join(header_line4)]
                head = '\n'.join(full_header)
                fh = open(full_file_output_name, 'w')
                fh.write(head)
                fh.close()
                # optionally h
                df_stuff.to_csv(full_file_output_name, mode='a', index=False, header=False)
    elif save_tail == True:
        # Similar but nearly the same for tailing.
        df_for_concat = []
        if output_format_csi == True:
            header_line1 = ['TOA5', '']
            header_line2 = ['TIMESTAMP']
            header_line3 = ['TS']
            header_line4 = ['']
        for station in glom_full['data_files']:
            station_object = input_timeseries()
            station_object.set_prop('input_csv', station['input_csv'])
            station_object.set_prop('alt_header_title', station['alt_header_title'])
            station_object.read_in_data_file_combined()
            station_object.subset_tail(rows_to_tail)
            station_object.convert_2_pandas()
            df_for_concat.append(station_object.csv_df)
            if output_format_csi == True:
                header_line2.append(station_object.input_csv_header_line_2)
                header_line3.append(station_object.input_csv_header_line_3)
                header_line4.append(station_object.input_csv_header_line_4)
        # ok, files are read in...
        # now, group and save to file again.
        df_stuff = pandas.concat(df_for_concat, axis=1)

        # file saving...
        full_file_output_name = output_file_path + output_filename_root + '_tail.csv'
        if output_format_csi == False:
            df_stuff.to_csv(full_file_output_name, na_rep='6999.00')
        else:
            # Close enough.
            full_header = [','.join(header_line1), ','.join(header_line2), ','.join(header_line3),
                           ','.join(header_line4)]
            csv_2_list = full_header
            csv_data = df_stuff.to_csv(path_or_buf=None, header=False)
            csv_data_list = csv_data.split('\n')
            for row in csv_data_list :
                row_list = row.split(',')
                csi_datestring = '"' + row_list[0] + '"'
                line_list = [csi_datestring]
                for element in row_list[1:] :
                    line_list.append(element)
                csv_2_list.append(','.join(line_list))

            fh = open(full_file_output_name, 'w')
            fh.write('\n'.join(csv_2_list))
            fh.close()
#            df_stuff.to_csv(full_file_output_name, mode='a', index=False, header=False)

if __name__ == '__main__':
  main()
