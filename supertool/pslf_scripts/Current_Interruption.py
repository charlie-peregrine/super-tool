from PSLF_PYTHON import *
from supertool.pslf_scripts.Super_Tool import *


###################################################################################################
#   Program: Current_Interruption.py
# 
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
# 
#   Revisions:
#   -10/11/2023 convert from epcl to python - Phase 1
#   -11/03/2023 convert from epcl to python - Phase 2 - solve save case
# 
#   Description:
#   -Opens the unit breaker to simulate a current interrruption test
#   -Copy Super_Tool.py into same directory as Current_Interruption.py
# 
###################################################################################################


def run(test, no_gui=False):

    #--------------------------------------------------------------------------------------------------
    # Configure for your test with the following parameters
    #--------------------------------------------------------------------------------------------------

    dyd_filename    = test.attrs["dyd_filename"].get()      # "U1.dyd"
    sav_filename    = test.attrs["sav_filename"].get()      # "02_U1_CI.sav"
    chf_filename    = test.attrs["chf_filename"].get()      # "02_U1_CI_sim_v23.chf"
    csv_filename    = test.attrs["csv_filename"].get()      # "02_U1_CI_sim_v23.csv"
    rep_filename    = test.attrs["rep_filename"].get()      # "Rep.rep"
    tripTimeInSecs  = test.attrs["tripTimeInSecs"].get()    # 2.0
    totTimeInSec    = test.attrs["totTimeInSec"].get()      # 36
    PSS_On          = test.attrs["PSS_On"].get()            # 0             # 0:disable PSS model, 1: enable PSS model */
    change_Pref     = test.attrs["change_Pref"].get()       # 1             # 1:Change Pref after breaker opens, 0: no change */
    offline_Pref    = test.attrs["offline_Pref"].get()      # 0.004         # note GGOV model uses 1 as base offline while HYG3 and IEEE1 use 0 */
    change_Vref     = test.attrs["change_Vref"].get()       # 0             # 1:Change Vref after breaker opens, 0: no change */
    offline_Vref    = test.attrs["offline_Vref"].get()      # 0.79
    AVR_On          = test.attrs["AVR_On"].get()            # 0             # 0: Exciter in Manual, 1: Exciter in Auto */
    set_loadflow    = test.attrs["set_loadflow"].get()      # False      # If TRUE, initializes sav case with the below parameters if FALSE, loads existing sav case.
    save_loadflow   = test.attrs["save_loadflow"].get()     # False     # If TRUE, overwrites sav_filename with new set_loadflow solution. If FALSE, leaves sav_filename as is.  

    #----------------------------------
    # loadflow Parameters
    #----------------------------------

    Pinit           = test.attrs["Pinit"].get()     # 1.49  # MW
    Qinit           = test.attrs["Qinit"].get()     # -5.25  # MVAR
    MVAbase         = test.attrs["MVAbase"].get()   # 206.0

    Vinit           = test.attrs["Vinit"].get()     # 13.266  # kV
    Vbase           = test.attrs["Vbase"].get()     # 13.8    # kV
    Zbranch         = test.attrs["Zbranch"].get()   # 0.123    # pu

    #--------------------------------------------------------------------------------------------------

    # gets the project directory of this file
    project_directory = os.path.dirname(os.path.realpath(__file__))

    SuperTool.launch_Pslf(project_directory, silent=no_gui)

    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")
    SuperTool.print_to_pslf("--------------------- Starting Current Interruption Test Simulation ---------------------")
    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------\n")

    SuperTool.psds()
    SuperTool.getf(sav_filename)
    SuperTool.setf(Pinit,Qinit,MVAbase,Vinit,Vbase,Zbranch,set_loadflow,save_loadflow,sav_filename)
    SuperTool.soln(0)
    SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)

    dp = DynamicsParameters()  # gets all the dynamics parameters
    dp.Delt = 0.0021

    SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)

    # Turn off PSS if not used in the simulation                             
    if(PSS_On==0):
        SuperTool.turn_off_pss(dp)
        SuperTool.print_to_pslf("PSS OFF")


    # Turn off PSS if not used in the simulation                             
    if(AVR_On==0):
        for i in range(dp.Nmodels):
            min = Model[i].ModLibNo
            if(ModelLibrary[min].Type == "x"):              # searches for exciter models 
                Model[i].St = 0                             # sets status of the exciter model to disabled.
                Pslf.print_to_pslf("AVR OFF\n")


    # Get impedance before current interruption as a debug message 
    i = Pslf.record_index(1,1,1,2,"1",1, -1)
    X = Secdd[i].Zsecx 

    dp.Conv_Mon = 0                     # set to 1 to display convergence monitor
    dp.Nplot = 1                        # save data every cycle
    dp.Nscreen = 100                    # display values on screen every 0.5 second
    dp.Tpause = tripTimeInSecs          # pauses after this amount of time

    ret = Pslf.run_dyn()

    Secdd[0].Zsecx = 99999.0
    Pslf.print_to_pslf("\n Breaker Open  \n")


    # As needed changing load and voltage reference
    nMod = Pslf.model_index(1,"gentpj",1,-1,"1 ",1,-1)
    k = Model[nMod].K

    if(change_Pref ==1):
        SuperTool.print_to_pslf("--- Changing Pref from ", GeneratorInitialConditions[k].Pref, " to ", offline_Pref)
        GeneratorInitialConditions[k].Pref = offline_Pref

    if(change_Vref ==1):
        SuperTool.print_to_pslf("--- Changing Vref from ", GeneratorInitialConditions[k].Vref, " to ", offline_Vref)
        GeneratorInitialConditions[k].Vref = offline_Vref

    dp.Nplot = 1                        # save data every cycle
    dp.Nscreen = 400                    # display values on screen every 0.5 second
    dp.Tpause = totTimeInSec            # pauses after this amount of time

    ret = Pslf.run_dyn()
    ret = Pslf.end_dyn_run()

    # attempts to create csv file
    SuperTool.chf_to_csv(csv_filename)

    SuperTool.print_to_pslf("\n-----------------------------------------------------------------------------------------")
    SuperTool.print_to_pslf(" This Current Interruption Test used the following:")
    SuperTool.print_to_pslf("System Impedance = ", X)

    if(PSS_On==1):
        SuperTool.print_to_pslf("PSS On for simulations")
    else:
        SuperTool.print_to_pslf("PSS Off for simulations")

    if(AVR_On==1):
        SuperTool.print_to_pslf("Exciter in Auto for simulations")
    else:
        SuperTool.print_to_pslf("Exciter in Manual for simulations")

    SuperTool.print_to_pslf("Sav Filename:      ", sav_filename)
    SuperTool.print_to_pslf("Dyd Filename:      ", dyd_filename)
    SuperTool.print_to_pslf("Chf Filename:      ", chf_filename)
    SuperTool.print_to_pslf("Csv Filename:      ", csv_filename)
    SuperTool.print_to_pslf("Rep Filename:      ", rep_filename)
    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")

    print("Finished running Current_Interruption.py Script!\n")
