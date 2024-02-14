from PSLF_PYTHON import *
from supertool.pslf_scripts.Super_Tool import *


###################################################################################################
#   Program: Voltage_Reference.py
# 
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
# 
#   Revisions:
#   -10/11/2023 convert from epcl to python - Phase 1
#   -10/16/2023 convert from epcl to python - Phase 2 - solve save case
# 
#   Description:
#   -Steps the voltage reference into the AVR
#   -copy Super_Tool.py into same directory as Voltage_Reference.py
# 
###################################################################################################

def run(test, no_gui=False):

#--------------------------------------------------------------------------------------------------
# Configure for your test with the following parameters
#--------------------------------------------------------------------------------------------------

    dyd_filename        = test.attrs["dyd_filename"].var.get()      # "HCPR1.dyd"
    sav_filename        = test.attrs["sav_filename"].var.get()      # "HCPR1_VR_P0_new.sav"
    chf_filename        = test.attrs["chf_filename"].var.get()      # "HCPR1_VR_P0_new_sim.chf"
    csv_filename        = test.attrs["csv_filename"].var.get()      # "HCPR1_VR_P0_new_sim.csv"
    rep_filename        = test.attrs["rep_filename"].var.get()      # "Rep.rep"
    StepTimeInSecs      = test.attrs["StepTimeInSecs"].var.get()    # 1.7
    UpStepInPU          = test.attrs["UpStepInPU"].var.get()        # 0.02
    DnStepInPU          = test.attrs["DnStepInPU"].var.get()        # 0.02
    StepLenInSecs       = test.attrs["StepLenInSecs"].var.get()     # 9.0
    TotTimeInSecs       = test.attrs["TotTimeInSecs"].var.get()     # 15
    PSS_On              = test.attrs["PSS_On"].var.get()            # 0                  # 0:disable PSS model, 1: enable PSS model 
    SysFreqInHz         = test.attrs["SysFreqInHz"].var.get()       # 60.00            
    SimPtsPerCycle      = test.attrs["SimPtsPerCycle"].var.get()    # 8.0  
    set_loadflow        = test.attrs["set_loadflow"].var.get()      # False      # If TRUE, initializes sav case with the below parameters if FALSE, loads existing sav case.
    save_loadflow       = test.attrs["save_loadflow"].var.get()     # False     # If TRUE, overwrites sav_filename with new set_loadflow solution. If FALSE, leaves sav_filename as is.  
    Pinit               = test.attrs["Pinit"].var.get()             # 118.85  # MW          #----------------------------------
    Qinit               = test.attrs["Qinit"].var.get()             # -1.98  # MVAR         # <- loadflow Parameters
    MVAbase             = test.attrs["MVAbase"].var.get()           # 145.0                 #----------------------------------
    Vinit               = test.attrs["Vinit"].var.get()             # 14.585  # kV
    Vbase               = test.attrs["Vbase"].var.get()             # 14.5    # kV
    Zbranch             = test.attrs["Zbranch"].var.get()           # 0.09    # pu
    PFtest              = False                                     # if the test is a PF test, then 
                                                                    #   1) the pfqrg model must come before the exciter model and after the generator model in the dyd         
                                                                    #   2) there must be no other pss model 
#--------------------------------------------------------------------------------------------------

    # Since pf model pfqrg is of type stabilizer model, pss must be enabled for an output to occur.
    if PFtest:
        PSS_On=True
        print("PFtest = 1, This is a power factor step test, which uses pfqrg model and no other PSS models. Adjust UpStepInPU and DnStepInPU until the output channel pf matches measured test data. ")
        ## add future functionality for error handling the presence of the pfqrg model? This script will likely barf if 
        ## 1) you try to run in PF mode w/o pfqrg model in the dyd and with other stabilizer models in service
        ## 2) you try to run in normal mode with pfqrg model. 
        ## maybe a good way to test for this is to check for all stabilizer models, and see if the model name corresponds to the specific test mode.

    # SimResScalar adjusts the number of points written to chf (and by extension the csv). if the total sim time is too large,
    # we run into memory overflow error specifically with dumping a large chf to csv. Thus, the solution is to downsample the output
    SimResScalar = round((TotTimeInSecs/250)+0.5)

    #NplotValue should be odd to reduce possiblility of simulation instability
    NplotValue = round(SimPtsPerCycle) * SimResScalar
    if NplotValue % 2 == 0:
        NplotValue -= 1
    print("Down-Sampling Factors - SimResScalar:", SimResScalar, "NplotValue:", NplotValue)


    # gets the project directory of this file and initialize the PSLF instance
    project_directory = os.path.dirname(os.path.realpath(__file__))
    #os.chdir(project_directory)
    SuperTool.launch_Pslf(project_directory, silent=no_gui) # @TODO add after calls and progress bar type stuff
    SuperTool.pwd()

    SuperTool.psds()
    SuperTool.getf(sav_filename)
    SuperTool.setf(Pinit,Qinit,MVAbase,Vinit,Vbase,Zbranch,set_loadflow,save_loadflow,sav_filename)
    SuperTool.soln(0)
    SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)   
    SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)


    # Turn off PSS if not used in the simulation
    dp = DynamicsParameters()                               # gets all the dynamics parameers
    if not PSS_On:
        SuperTool.turn_off_pss(dp)

    SuperTool.print_to_pslf("\n--- Establishing the Pre-Step State")
    dp.Delt = 1 / (SimPtsPerCycle * SysFreqInHz)                    # sets the delta time step 
    dp.Conv_Mon = 0                                                 # set to 1 to display convergence monitor
    dp.Nplot = NplotValue                                           # save data every # of cycle
    dp.Nscreen = round(SysFreqInHz * SimPtsPerCycle) * SimResScalar #  display values on screen every 0.5 second
    dp.Tpause = StepTimeInSecs                                      # pauses at the beginning of the voltage step
    ret = Pslf.run_dyn()

    SuperTool.print_to_pslf("\n--- Applying the Step")
    if not PFtest:
        GeneratorInitialConditions[0].Vref = GeneratorInitialConditions[0].Vref + UpStepInPU
    else:
        pfqrg_ref = Pslf.get_model_parameters(1, 1, -1, "1 ", 1, "pfqrg","ref")
        pfqrg_ref-=UpStepInPU
        Pslf.set_model_parameters(1, 1, -1,"1 ", 1,"pfqrg","ref", pfqrg_ref)
    dp.Tpause = StepTimeInSecs + StepLenInSecs
    ret = Pslf.run_dyn()

    SuperTool.print_to_pslf("\n--- Removing the Step")
    if not PFtest:
        GeneratorInitialConditions[0].Vref = GeneratorInitialConditions[0].Vref - DnStepInPU
    else:
        pfqrg_ref = Pslf.get_model_parameters(1, 1, -1, "1 ", 1, "pfqrg","ref")
        pfqrg_ref+=DnStepInPU
        Pslf.set_model_parameters(1, 1, -1,"1 ", 1,"pfqrg","ref", pfqrg_ref)

    dp.Tpause = TotTimeInSecs
    ret = Pslf.run_dyn()
    ret = Pslf.end_dyn_run()
    ret = SuperTool.chf_to_csv(csv_filename)

    SuperTool.print_to_pslf("\n-----------------------------------------------------------------------------------------")
    SuperTool.print_to_pslf("Previous Voltage Reference Step Simulation Used:")
    SuperTool.print_to_pslf("Positive Step Size:  ", UpStepInPU, " pu")
    SuperTool.print_to_pslf("Negative Step Size:  ", DnStepInPU, " pu")


    i = Pslf.record_index(1,1,1,2,"1",1, -1)
    SuperTool.print_to_pslf("System Impedance:    ", Secdd[i].Zsecx)

    if PSS_On:
        SuperTool.print_to_pslf("PSS Status:          On")
    else:
        SuperTool.print_to_pslf("PSS Status:          Off")


    SuperTool.print_to_pslf("Set loadflow?        ", bool(set_loadflow))
    SuperTool.print_to_pslf("Save loadflow?       ", bool(save_loadflow))
    SuperTool.print_to_pslf("Sav Filename:        ", sav_filename)
    SuperTool.print_to_pslf("Dyd Filename:        ", dyd_filename)
    SuperTool.print_to_pslf("Chf Filename:        ", chf_filename)
    SuperTool.print_to_pslf("Csv Filename:        ", csv_filename)
    SuperTool.print_to_pslf("Rep Filename:        ", rep_filename)
    SuperTool.print_to_pslf("-----------------------------------------------------------------------------------------")

    print("Finished running Voltage_Reference.py script!\n")

# run()