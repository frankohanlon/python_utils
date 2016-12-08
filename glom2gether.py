#!/usr/bin/python -tt

"""
Version two of glom together, uses pandas.
"""
import sys
import os
import csv
import pandas 
import ConfigParser

def main():
    """ Main Program Body
    """
    ###################################################################################
    ##  Read in the site configuration file                                          ##
    ###################################################################################

   #First we need to get the config file, or die if it hasn't been given

    try:
        configFile = sys.argv[1]
        print "\n##############################################################################"
        print "Running through: ", sys.argv[1]
        print "##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##"
    except IndexError:
        print """Needs Configuration File.  Enter like this:
        $ python datapro.py c:\\data\\atlas\\C1-grid\\c1-met_key.py.txt
        """
        sys.exit(1)

    # 1) initialize the config object
    keyfile = ConfigParser.SafeConfigParser()
    # 2) Read the config file...
    # ... Returns a dictionary of the keys and values in the configuration file
    readSuccess = keyfile.read([configFile])

    # if there was trouble reading the file error out here
    try:
        if not(readSuccess[0] == configFile):
            print "Could not read config file";
            sys.exit(1)
    except IndexError:
        print "Could not read config file";
        sys.exit(1)

    ###################################################################################
    ##  read in the data variable specific configuration file                        ##
    ###################################################################################
    try:
        csvFile = open(keyfile.get('main', 'glom_params_key_file'), 'r' )
    except Exception, e:
        print "Could not obtain station info: ", e
        sys.exit(1)
    csvReader = csv.DictReader(csvFile)
    siteList={}
    h = 0
    for row in csvReader:
        # row['StationName'] = the element in the first column
        siteList[h] = row
        h+=1
    # done with the key file

    csvFile.close()
    ###################################################################################
    ##  create necessary error & qc log directories  if they haven't been made before:       ##
    ###################################################################################
    if not os.path.exists(keyfile.get('main', 'error_log_dir')):
        os.mkdir(keyfile.get('main', 'error_log_dir'))
    if not os.path.exists(keyfile.get('main', 'qc_log_dir')):
        os.mkdir(keyfile.get('main', 'qc_log_dir'))

    all_df = []
    for element in siteList :
        in_file_name = siteList[element]['File_Loc']
        print "Input File: ", in_file_name
        ## Check to see if the input file exists
        if os.path.exists(in_file_name) :
            try :
                in_file_handle = open( in_file_name, 'r')
                data = in_file_handle.readlines()       
                delement = data[3].rstrip().split(',')[1]
                in_file_handle.close()
                # open current data file, read in the file ignoring the header and
                # then splitting the file into a 2D array by time and the first two data elements
                # (hourly data should have 2 data elements, daily data should have 3 data elements)
                df = pandas.read_csv(in_file_name, skiprows=3, index_col=0, infer_datetime_format=True) 
                df.rename(columns = {delement : siteList[element]['Output_Header_Line_2']}, inplace=True)
                all_df.append(df)
            except :
                print 'problem opening %s for reading.' % (in_file_name)
        else:
            print 'problem opening %s for reading.' % (in_file_name)

    # Now all the data has been read in.  On to the glomming.
    combined = pandas.concat(all_df,axis=1)
    combined.fillna(6999,inplace=True)
    try:
        outfile = keyfile.get('main', 'output_data_file')
        combined.to_csv(outfile, float_format='%.2f')
    except:    
        print 'error opening %s for writing' % (keyfile.get('main', 'output_data_file'))
    print "###########################################################################\n"
###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
