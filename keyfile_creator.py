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
        print """Needs Some information to run.  Enter like this:
             $ python trackarrays.py --infile=/var/site/uaf_sp/blueberry/data
             """
        sys.exit(1)
    for commandlinestuff in sys.argv :
        cl_param = commandlinestuff.split('=')
        if cl_param[0] == '--infile' :
            try:
                inputfile = cl_param[1]
                if (not os.path.exists(inputfile)) :
                    print 'problem finding input file, ', cl_param[0], '\n'
            except:
                print 'did not find valid input file'
                sys.exit(1)
        elif cl_param[0] == '--configpath' :
            configpath= str(cl_param[1])
        elif cl_param[0] == '--sitename' :
            sitename = cl_param[1]
        elif cl_param[0] == '--help' :
            print """
                  To correctly use this python utility:
             $ python trackarrays.py --infile=/var/site/uaf_sp/blueberry/data                  """
            sys.exit(1)



    ###################################################################################
    ##  Open the input file                                                          ##
    ###################################################################################
    try:
        ifile = open (inputfile, 'r')
        datafile = ifile.readlines()
        ifile.close()
    except:
        print 'problem opening %s for reading (input file)' % inputfile
        sys.exit(1)
    cwd = os.getcwd()    

    arraylist= []
    linearrays={}
    for lines in datafile :
        templine = lines.rstrip()
        linelist = lines.split(',')
        arrayid = linelist[0]
        strlen = len(linelist)
        key = str(arrayid) + "-" + str(strlen)
        if not key in arraylist :
            arraylist.append(key)
            linearrays[key] = templine
        
    for item in sorted(linearrays):
        print item, ' ', linearrays[item]
        linelist = linearrays[item].split(',')
        outfile = configpath + '/' + sitename + '_' + item + '_key.txt'
        [arrayid, arraylength] = item.split('-') 
        dirsplit = configpath.split('/')
        rootdir =  '/'.join(dirsplit[:-1]) + '/'
        paramfilename = configpath + '/' + sitename +'_'+ item + '_param_file' + '.csv'
        inputdirsplit = inputfile.split('/')
        if len(inputdirsplit) == 1 :
            # then need to prepend current working directory
            inputfile = os.getcwd() + '/' + inputfile

        # First create the key file
        outcontent = '[main]\n'
        outcontent += 'station_name = ' + sitename + '\n'
        outcontent += 'logger_type = CR10X\n'
        outcontent += 'arrays = ' + arraylength + '\n'
        outcontent += 'array_id = ' + arrayid + '\n\n\n'
        outcontent += 'input_data_file = ' + inputfile + '\n'
        outcontent += 'array_based_params_key_file = ' + paramfilename + '\n'
        outcontent += 'therm1 = null\ntherm2 = null\n\n'
        outcontent += 'output_dir = ' + rootdir + 'outputs/\n'
        outcontent += 'qc_log_dir = ' + rootdir + 'qc/\n'
        outcontent += 'error_log_dir = ' + rootdir + 'error/\n'        
        outcontent += 'bad_data_val = 6999\n\n'
        ofile = open(outfile, 'w')        
        ofile.write(outcontent)
        ofile.close()
        
        # Second, create the parameter file
        outcontent = 'd_element,Data_Type,Input_Array_Pos,Coef_1,Coef_2,Coef_3,Coef_4,Coef_5,Coef_6,Coef_7,Qc_Param_High,Qc_Param_Low,QC_Param_Step,Output_Header_Name,Ouput_Header_Units,Output_Header_Measurement_Type\n'
        row = 0
        for datapoint in linearrays[item].split(',') :
            rowstr = str(row)
            outcontent += str(datapoint) + ',num,' + rowstr + ',0,0,0,0,0,0,0,0,0,0,sensor,units,Avg\n'
            row +=1
        paramfile = open(paramfilename, 'w')
        paramfile.write(outcontent)
        paramfile.close()
###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
