#!/usr/bin/env python

import os
import sys



def main():
    """ Main Program Body
    """
    ###################################################################################
    ##  Read in the commandline parameters                                          ##
    ###################################################################################
    inputfile = ''
    try:
        extraparams = sys.argv[1]
    except IndexError:
        print ("""Needs Some information to run.  Enter like this:
             $ python trackarrays.py --infile=/home/bbusey/working_files/data/outputs/battery.csv
             """)
        sys.exit(1)
    for commandlinestuff in sys.argv :
        cl_param = commandlinestuff.split('=')
        if cl_param[0] == '--infile' :
            try:
                inputfile = cl_param[1]
                if not os.path.exists(inputfile) :
                    print ('problem finding input file, ', cl_param[0], '\n')
            except:
                print ('did not find valid input file')
                sys.exit(1)
        elif cl_param[0] == '--help' :
            print ("""
                  To correctly use this python utility:
                  $ python 6999filler.py --infile=/home/bbusey/working_files/data/outputs/battery.csv
                  """)
            sys.exit(1)



    ###################################################################################
    ##  Open the input file                                                          ##
    ###################################################################################
    try:
        ifile = open (inputfile, 'r')
        datafile = ifile.readlines()
        ifile.close()
    except:
        print ('problem opening %s for reading (input file)' % inputfile)
        sys.exit(1)
    
    arraylist= []
    linearrays={}
    for lines in datafile :
        linelist = lines.split(',')
        arrayid = linelist[0]
        strlen = len(linelist)
        key = str(arrayid) + "-" + str(strlen)
        if not key in arraylist :
            arraylist.append(key)
            linearrays[key] = lines
        

    for item in sorted(linearrays):
        print (item, ' ', linearrays[item])
    print ('\n'.join(arraylist))
###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
