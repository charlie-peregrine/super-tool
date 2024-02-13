from PSLF_PYTHON import *
from supertool.pslf_scripts.Super_Tool import *


###################################################################################################
#   Program: Speed_Reference.py
# 
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
# 
#   Revisions:
#   -10/11/2023 convert from epcl to python - Phase 1
#   -10/16/2023 convert from epcl to python - Phase 2 - solve save case
# 
#   Description:
#   -Injects a speed reference step into the ggov3 model via the t1-t5, n1-n5 model point pairs
#   -copy Super_Tool.py into same directory as Speed_Reference.py
# 
###################################################################################################

def run(test, no_gui=False):
    # initalizes some global variables
    TotalSteps = 6
    StepTimeInSecs=[0 for x in range(TotalSteps)]
    StepSizeInPu=[0 for x in range(TotalSteps)]

    #OneLine=[[0 for x in range(1)] for y in range(500)]
    #print(OneLine)


    #--------------------------------------------------------------------------------------------------
    # Configure for your test with the following parameters
    #--------------------------------------------------------------------------------------------------

    dyd_filename    = test.attrs["dyd_filename"].var.get()       #"Dania71.dyd"
    sav_filename    = test.attrs["sav_filename"].var.get()       #"urmom2.sav"
    chf_filename    = test.attrs["chf_filename"].var.get()       #"CTG71_GOV_LC0_sim1.chf"
    csv_filename    = test.attrs["csv_filename"].var.get()       #"CTG71_GOV_LC0_sim1.csv"
    rep_filename    = test.attrs["rep_filename"].var.get()       #"Rep.rep"


    StepTimeInSecs[1]  = test.attrs["StepTimeInSecs1"].var.get()       #107.64
    StepTimeInSecs[2]  = test.attrs["StepTimeInSecs2"].var.get()       #107.65
    StepTimeInSecs[3]  = test.attrs["StepTimeInSecs3"].var.get()       #172.6
    StepTimeInSecs[4]  = test.attrs["StepTimeInSecs4"].var.get()       #172.65
    StepTimeInSecs[5]  = test.attrs["StepTimeInSecs5"].var.get()       #200
    TotalSimTime       = test.attrs["TotalSimTime"].var.get()       #285.12


    StepSizeInPu[1]    = test.attrs["StepSizeInPu1"].var.get()       #-0.00
    StepSizeInPu[2]    = test.attrs["StepSizeInPu2"].var.get()       #0.002589
    StepSizeInPu[3]    = test.attrs["StepSizeInPu3"].var.get()       #0.002589 
    StepSizeInPu[4]    = test.attrs["StepSizeInPu4"].var.get()       #0.000
    StepSizeInPu[5]    = test.attrs["StepSizeInPu5"].var.get()       #-0.000


    SysFreqInHz        = test.attrs["SysFreqInHz"].var.get()       #60.00            
    SimPtsPerCycle     = test.attrs["SimPtsPerCycle"].var.get()       #4.0  


    set_loadflow       = test.attrs["set_loadflow"].var.get()       #True      # If TRUE, initializes sav case with the below parameters if FALSE, loads existing sav case.
    save_loadflow      = test.attrs["save_loadflow"].var.get()       #False     # If TRUE, overwrites sav_filename with new set_loadflow solution. If FALSE, leaves sav_filename as is.  

    #----------------------------------
    # loadflow Parameters
    #----------------------------------

    Pinit               = test.attrs["Pinit"].var.get()       #380.0 # MW
    Qinit               = test.attrs["Qinit"].var.get()       #-3.19  # MVAR
    MVAbase             = test.attrs["MVAbase"].var.get()       #579.0

    Vinit               = test.attrs["Vinit"].var.get()       #25.29  # kV
    Vbase               = test.attrs["Vbase"].var.get()       #24.0   # kV
    Zbranch             = test.attrs["Zbranch"].var.get()       #0.0327 # pu

    GenBusID			= test.attrs["GenBusID"].var.get()       #"1 "

    #--------------------------------------------------------------------------------------------------


    # dont change these values. Theyre not used in the speed step.
    StepTimeInSecs[0]  = 0
    StepSizeInPu[0]    = 0


    # gets the project directory of this file
    project_directory = os.path.dirname(os.path.realpath(__file__))

    SuperTool.launch_Pslf(project_directory, silent=no_gui)
    SuperTool.pwd()


    # checks if time steps are enterred in ascending order
    for i in range(TotalSteps-1):
        #print("i: ", i)
        #print("TimeStepInSec[i+1] ", StepTimeInSecs[i+1])
        #print("TimeStepInSec[i] ", StepTimeInSecs[i])
        if(StepTimeInSecs[i+1]<StepTimeInSecs[i]):
            SuperTool.fatal_error("TimeStepInSec[] values must be in ascending order.")

    # checks if total simulation time is larger than last step
    if(TotalSimTime<StepTimeInSecs[TotalSteps-1]):
        SuperTool.fatal_error("Total simulation time must be greater than last step time.")


    SuperTool.psds()
    SuperTool.getf(sav_filename) 
    SuperTool.setf(Pinit,Qinit,MVAbase,Vinit,Vbase,Zbranch,set_loadflow,save_loadflow,sav_filename)
    SuperTool.soln(0)
    SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)


    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","t1", StepTimeInSecs[1])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","t2", StepTimeInSecs[2])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","t3", StepTimeInSecs[3])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","t4", StepTimeInSecs[4])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","t5", StepTimeInSecs[5])
    
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","n1", StepSizeInPu[1])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","n2", StepSizeInPu[2])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","n3", StepSizeInPu[3])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","n4", StepSizeInPu[4])
    ret = Pslf.set_model_parameters(1, 1, -1,GenBusID, 1,"ggov3","n5", StepSizeInPu[5])

    SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)

    dp = DynamicsParameters()                       # gets all the dynamics parameters
    dp.Delt = 1 / (SimPtsPerCycle * SysFreqInHz)    # sets the delta time step 
    dp.Conv_Mon = 0                                 # set to 1 to display convergence monitor
    dp.Nplot = 20                                   # save data every cycle
    dp.Nscreen = 150                                #  display values on screen every 0.5 second

    # SuperTool.set_gens_ID(dp)

    #   ----------------------------------------------------------
    #   Run the Simulation ---------------------------------------
    #   ----------------------------------------------------------

    SuperTool.print_to_pslf("--- Running some prestep simulation ---")
    dp.Tpause = TotalSimTime                              # pauses at the beginning of the voltage step
    ret = Pslf.run_dyn()
    ret = Pslf.end_dyn_run()
    ret = SuperTool.chf_to_csv(csv_filename)


    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")
    SuperTool.print_to_pslf("Set loadflow?   ", bool(set_loadflow))
    SuperTool.print_to_pslf("Save loadflow?  ", bool(save_loadflow))
    SuperTool.print_to_pslf("Sav Filename:   ", sav_filename)
    SuperTool.print_to_pslf("Dyd Filename:   ", dyd_filename)
    SuperTool.print_to_pslf("Chf Filename:   ", chf_filename)
    SuperTool.print_to_pslf("Csv Filename:   ", csv_filename)
    SuperTool.print_to_pslf("Rep Filename:   ", rep_filename)
    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")

    i = Pslf.record_index(1,1,1,2,"1",1, -1)
    SuperTool.print_to_pslf("System Impedance: ", Secdd[i].Zsecx)

    for i in range(TotalSteps):
        SuperTool.print_to_pslf("Pref Step:\t", StepSizeInPu[i], " pu @ ", StepTimeInSecs[i], " seconds")

    SuperTool.print_to_pslf("Total Sim Time:\t", TotalSimTime, " seconds")
    SuperTool.print_to_pslf("\n-----------------------------------------------------------------------------------------")

    print("Finished running Speed_Reference.py script!\n")