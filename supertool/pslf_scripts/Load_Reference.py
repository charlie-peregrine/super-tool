from PSLF_PYTHON import *
from supertool.pslf_scripts.Super_Tool import *


###################################################################################################
#   Program: Load_Reference.py
#   
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
# 
#   Revisions:
#   -10/11/2023 convert from epcl to python - Phase 1
#   -10/16/2023 convert from epcl to python - Phase 2 - solve save case
# 
#   Description:
#   -Injects a load reference setpoint into a governor model
#   -Copy Super_Tool.py into same directory as Load_Reference.py
# 
###################################################################################################


def run(test, no_gui=False):
    # initalizes some global variables
    TotalSteps = 6
    StepTimeInSecs=[0.0 for x in range(TotalSteps)]
    StepSizeInPu=[0.0 for x in range(TotalSteps)]

    #OneLine=[[0 for x in range(1)] for y in range(500)]
    #print(OneLine)


    #--------------------------------------------------------------------------------------------------
    # Configure for your test with the following parameters
    #--------------------------------------------------------------------------------------------------

    dyd_filename    = test.attrs["dyd_filename"].get()       #"HCPR3.dyd" # "HCPR1.dyd"
    sav_filename    = test.attrs["sav_filename"].get()       #"HCPR3_VStepP02_P0.sav" # "HCPR1_GOV.sav"
    chf_filename    = test.attrs["chf_filename"].get()       #"HCPR3_VStepP02_P0.chf" # "HCPR1_GOV_new_sim.chf"
    csv_filename    = test.attrs["csv_filename"].get()       #"HCPR3_VstepP02_P0_sim.csv" # "HCPR1_GOV_new_sim.csv"
    rep_filename    = test.attrs["rep_filename"].get()       #"HCPR3_VStepP-2_P0.rep" # "Rep.rep"


    StepTimeInSecs[0]  = test.attrs["StepTimeInSecs0"].get()       #8.2
    StepTimeInSecs[1]  = test.attrs["StepTimeInSecs1"].get()       #491.9
    StepTimeInSecs[2]  = test.attrs["StepTimeInSecs2"].get()       #700
    StepTimeInSecs[3]  = test.attrs["StepTimeInSecs3"].get()       #700
    StepTimeInSecs[4]  = test.attrs["StepTimeInSecs4"].get()       #700
    StepTimeInSecs[5]  = test.attrs["StepTimeInSecs5"].get()       #700
    TotalSimTime       = test.attrs["TotalSimTime"].get()       #971

    StepSizeInPu[0]    = test.attrs["StepSizeInPu0"].get()       #0.005
    StepSizeInPu[1]    = test.attrs["StepSizeInPu1"].get()       #-0.005
    StepSizeInPu[2]    = test.attrs["StepSizeInPu2"].get()       #0.000
    StepSizeInPu[3]    = test.attrs["StepSizeInPu3"].get()       #-0.000 
    StepSizeInPu[4]    = test.attrs["StepSizeInPu4"].get()       #0.000
    StepSizeInPu[5]    = test.attrs["StepSizeInPu5"].get()       #-0.000


    SysFreqInHz        = test.attrs["SysFreqInHz"].get()       #60.00            
    SimPtsPerCycle     = test.attrs["SimPtsPerCycle"].get()       #4.0  

    set_loadflow       = test.attrs["set_loadflow"].get()       #True      # If TRUE, initializes sav case with the below parameters if FALSE, loads existing sav case.
    save_loadflow      = test.attrs["save_loadflow"].get()       #False     # If TRUE, overwrites sav_filename with new set_loadflow solution. If FALSE, leaves sav_filename as is.  

    #----------------------------------
    # loadflow Parameters
    #----------------------------------

    Pinit               = test.attrs["Pinit"].get()       #121.3  # MW
    Qinit               = test.attrs["Qinit"].get()       #-1.98  # MVAR
    MVAbase             = test.attrs["MVAbase"].get()       #145.0

    Vinit               = test.attrs["Vinit"].get()       #14.585  # kV
    Vbase               = test.attrs["Vbase"].get()       #14.5    # kV
    Zbranch             = test.attrs["Zbranch"].get()       #0.09    # pu

    #--------------------------------------------------------------------------------------------------


    # gets the project directory of this file
    project_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(project_directory)
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
        SuperTool.fatal_error("TotalSimTime value must be greater than last StepTimeInSecs[] time.")

    SuperTool.psds() 
    SuperTool.getf(sav_filename)
    SuperTool.setf(Pinit,Qinit,MVAbase,Vinit,Vbase,Zbranch,set_loadflow,save_loadflow,sav_filename)
    SuperTool.soln(0)
    SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)
    SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)

    dp = DynamicsParameters()                               # gets all the dynamics parameters
    dp.Delt = 1 / (SimPtsPerCycle * SysFreqInHz)            # sets the delta time step 
    dp.Conv_Mon = 0                                         # set to 1 to display convergence monitor
    dp.Nplot = 20                      # save data every cycle
    dp.Nscreen = 150        #  display values on screen every 0.5 second


    #   ----------------------------------------------------------
    #   Run the Simulation ---------------------------------------
    #   ----------------------------------------------------------

    SuperTool.print_to_pslf("--- Running some prestep simulation ---")
    dp.Tpause = StepTimeInSecs[0]                              # pauses at the beginning of the voltage step

    ret = Pslf.run_dyn()

    for i in range(TotalSteps):
        SuperTool.print_to_pslf("--- Applying a ",StepSizeInPu[i]," pu Step in Pref to current value of ",GeneratorInitialConditions[0].Pref)

        GeneratorInitialConditions[0].Pref = GeneratorInitialConditions[0].Pref + StepSizeInPu[i] # genbc[0].pref equivalent

        if(i<TotalSteps-1):
            dp.Tpause = StepTimeInSecs[i+1]
            SuperTool.print_to_pslf("StepTimeInSec[i+1]: ", StepTimeInSecs[i+1])
        else:
            dp.Tpause = TotalSimTime
        
        ret = Pslf.run_dyn()
        if(ret!=0):
            SuperTool.fatal_error("The dynamics run malfunctioned.")

    # attempts to create csv file
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

    for i in range(TotalSteps-1):
        SuperTool.print_to_pslf("Pref Step: ", StepSizeInPu[i]," pu @ ", StepTimeInSecs[i], " seconds")


    SuperTool.print_to_pslf("Total Sim Time:\t", TotalSimTime," seconds")
    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")

    print("Finished running Load_Reference.py script!\n")