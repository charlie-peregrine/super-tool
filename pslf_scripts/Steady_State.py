from PSLF_PYTHON import *
from Super_Tool import *
import csv

###################################################################################################
#   Program: Steady_State.py
#
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
#
#   Revisions:
#   -10/11/2023 convert from epcl to python - Phase 1
#   -11/03/2023 Phase 2
#
#   Description:
#   -solves multiple P,Q,V load flows for a v-curve load ramp, and saves into a csv file
#   -copy Super_Tool.py into same directory as Steady_State.py
# 
###################################################################################################


#--------------------------------------------------------------------------------------------------
# Configure for your test with the following parameters
#--------------------------------------------------------------------------------------------------

dyd_filename    = "HCPR1.dyd"
sav_filename    = "HCPR1_LR.sav"
chf_filename    = "HCPR1_LR_new_sim.chf"
rep_filename    = "Rep.rep"

in_filename     = "HCPR1_LR_IN.csv"
out_filename    = "HCPR1_LR_OUT_new.csv"

out_casename    = "HCPR1_LR.txt"

if_base         = 740
if_res          = 0.0
SaveCaseFiles   = 0 # generally leave as 0
UseGenField     = 0 # set this to '1' if you want to use generator field even for brushless
#mva_base        = 145.0

#--------------------------------------------------------------------------------------------------


# initialize some global variables
Ifd_A = 0.0
Ifd_pu = 0.0
Efd_pu = 0.0
ExcModIndex = 0


# gets the project directory of this file and initialize the PSLF instance
project_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(project_directory)
SuperTool.launch_Pslf(project_directory)

# print to PSLF console
SuperTool.pwd()
ret = SuperTool.psds()   


# opens the input csv for reading, puts into csvInData 2d array
try:
    #csvfile = open(os.path.join(current_directory,in_filename), 'r')
    #csvData = csvfile.readlines()

    # loads values of the input csv file into a 2d array
    f = open(os.path.join(project_directory,in_filename), 'r')
    csvInFile = csv.reader(f, delimiter=",")
    csvInData = list(csvInFile)
except:
    errmsg = "*** Error: unable to open input .csv file. Exitting... "
    SuperTool.fatal_error(errmsg)


# Gets the Nominal Generator Bus Voltage and branch impedance from the first two lines of the CSV Input File
Vbase = float(csvInData[0][0])
Zbranch = float(csvInData[1][0])


#  This opens the CSV Output File for writing
try:
    f = open(os.path.join(project_directory,out_filename), "w", newline='')
    csvOutFile = csv.writer(f)
    csvHeader = ['Load Point','P (MW)','Q (MVAR)','Vt-desired (pu)','Vt-sim (pu)','Vfd (pu)','Ifd (pu)','BusV-sched (pu)','Ifd (A)']
    csvOutFile.writerow(csvHeader)
except:
    SuperTool.fatal_error("Unable to open output .csv file.")

ret = SuperTool.getf(sav_filename)
ret = SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)
#Generator[0].Mbase = mva_base # sets generator mva base                                                       

# Finds the exciter model name
excModName = ""
dp = DynamicsParameters()   # gets all the dynamics parameters
for i in range(dp.Nmodels): # searches through the models to find model library number
        mln = Model[i].ModLibNo 
        if((ModelLibrary[mln].Type=="x") & ('oel1' not in ModelLibrary[mln].Name)):              # searches for exciter models "x" that arent oel1
            excModName = ModelLibrary[mln].Name
            excModIndex = i

if excModName == "":
    errmsg = "*** Error: unable to find exciter model. Exitting..."
    SuperTool.fatal_error(errmsg)

csvRowIndex=2
while(TRUE):
    # sets the measured generator quantities from the csv row into local variables
    Pgen  = float(csvInData[csvRowIndex][0])
    Qgen  = float(csvInData[csvRowIndex][1])
    Vtgen = float(csvInData[csvRowIndex][2])

    SuperTool.print_to_pslf("\nLoad Point #",csvRowIndex-1)
    SuperTool.print_to_pslf("P: ",Pgen," Q: ",Qgen," Vt: ",Vtgen)

    SuperTool.getf(sav_filename)
    SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)
    
    # This initializes bus parameters for the loadflow
    SuperTool.set_loadflow_parameters(Pgen,Qgen,Vtgen,Vbase,Zbranch)
    ret = SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)

    #  Retrieve Ifd_pu and Efd_pu for writing to output csv file
    if(UseGenField!=0):
        Ifd_pu = GeneratorInitialConditions[0].Ladifd
        Efd_pu = GeneratorInitialConditions[0].Efd
    elif('esac1a' in excModName):
        Ifd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
        Efd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vr")
    elif('esac2a' in excModName):
        Ifd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
        Efd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vr")
    elif('esac2' in excModName):
        Ifd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
        Efd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vr")
    elif('esac7b' in excModName):
        Ifd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
        Efd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vr")
    elif('esac8b' in excModName):
        Ifd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
        Efd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vr")
    elif('rexs' in excModName):
        # note that rexs model exciter field quantities have different names in model than the esac models
        Ifd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"ife")
        Efd_pu = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
    else:
        Ifd_pu = GeneratorInitialConditions[0].Ladifd
        Efd_pu = GeneratorInitialConditions[0].Efd

    # calculates Exciter Field in amps
    Ifd_A = Ifd_pu * (if_base-if_res)

    # write to the csv
    csvOutData = [csvRowIndex-1, Pgen, Qgen, round(Vtgen,3), round(Bus[0].Vm,3), round(Efd_pu,5), round(Ifd_pu,5), round(Bus[1].Vsched,3),round(Ifd_A,2)]
    csvOutFile.writerow(csvOutData)
 
    SuperTool.print_to_pslf("\n-----------------------------------------------------------------------------------------")
    
    # if no more rows in the .csv 2d data array, we are complete
    csvRowIndex+=1
    if(csvRowIndex>=len(csvInData)):
        break

SuperTool.print_to_pslf("\n-----------------------------------------------------------------------------------------")
SuperTool.print_to_pslf("Sav Filename:      ", sav_filename)
SuperTool.print_to_pslf("Dyd Filename:      ", dyd_filename)
SuperTool.print_to_pslf("Chf Filename:      ", chf_filename)
SuperTool.print_to_pslf("Csv in Filename:   ", in_filename)
SuperTool.print_to_pslf("Csv out Filename:  ", out_filename)
SuperTool.print_to_pslf("Rep Filename:      ", rep_filename)
SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")


print("Finished running Steady_State.py Script!\n")

