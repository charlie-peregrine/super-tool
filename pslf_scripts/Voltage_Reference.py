from PSLF_PYTHON import *
from Super_Tool import *


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


#--------------------------------------------------------------------------------------------------
# Configure for your test with the following parameters
#--------------------------------------------------------------------------------------------------

dyd_filename    = "HCPR1.dyd"
sav_filename    = "HCPR1_VR_P0_new.sav"
chf_filename    = "HCPR1_VR_P0_new_sim.chf"
csv_filename    = "HCPR1_VR_P0_new_sim.csv"
rep_filename    = "Rep.rep"
StepTimeInSecs  = 1.7
UpStepInPU      = 0.02
DnStepInPU      = 0.02
StepLenInSecs   = 9.0
TotTimeInSecs   = 15
PSS_On          = 0                                 # 0:disable PSS model, 1: enable PSS model 
SysFreqInHz     = 60.00            
SimPtsPerCycle  = 8.0  

set_loadflow       = False      # If TRUE, initializes sav case with the below parameters if FALSE, loads existing sav case.
save_loadflow      = False     # If TRUE, overwrites sav_filename with new set_loadflow solution. If FALSE, leaves sav_filename as is.  

#----------------------------------
# loadflow Parameters
#----------------------------------

Pinit               = 118.85  # MW
Qinit               = -1.98  # MVAR
MVAbase             = 145.0

Vinit               = 14.585  # kV
Vbase               = 14.5    # kV
Zbranch             = 0.09    # pu

#--------------------------------------------------------------------------------------------------


# gets the project directory of this file and initialize the PSLF instance
project_directory = os.path.dirname(os.path.realpath(__file__))
#os.chdir(project_directory)
SuperTool.launch_Pslf(project_directory)
SuperTool.pwd()

SuperTool.psds()
SuperTool.getf(sav_filename)
SuperTool.setf(Pinit,Qinit,MVAbase,Vinit,Vbase,Zbranch,set_loadflow,save_loadflow,sav_filename)
SuperTool.soln(0)
SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)   
SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)


# Turn off PSS if not used in the simulation
dp = DynamicsParameters()                               # gets all the dynamics parameers
if(PSS_On==0):
    SuperTool.turn_off_pss(dp)

SuperTool.print_to_pslf("\n--- Establishing the Pre-Step State")
dp.Delt = 1 / (SimPtsPerCycle * SysFreqInHz)            # sets the delta time step 
dp.Conv_Mon = 0                                         # set to 1 to display convergence monitor
dp.Nplot = round(SimPtsPerCycle)                        # save data every cycle
dp.Nscreen = round(SysFreqInHz * SimPtsPerCycle)        #  display values on screen every 0.5 second
dp.Tpause = StepTimeInSecs                              # pauses at the beginning of the voltage step
ret = Pslf.run_dyn()

SuperTool.print_to_pslf("\n--- Applying the Step")
GeneratorInitialConditions[0].Vref = GeneratorInitialConditions[0].Vref + UpStepInPU
dp.Nplot = 1
dp.Nscreen = round(SysFreqInHz*SimPtsPerCycle)
dp.Tpause = StepTimeInSecs + StepLenInSecs
ret = Pslf.run_dyn()

SuperTool.print_to_pslf("\n--- Removing the Step")
GeneratorInitialConditions[0].Vref = GeneratorInitialConditions[0].Vref - DnStepInPU
dp.Tpause = TotTimeInSecs
ret = Pslf.run_dyn()
ret = Pslf.end_dyn_run()
ret = SuperTool.chf_to_csv(csv_filename)

SuperTool.print_to_pslf("\n-----------------------------------------------------------------------------------------")
SuperTool.print_to_pslf("Previous Voltage Reference Step Simulation Used:")
SuperTool.print_to_pslf("Positive Step Size:  ", UpStepInPU," pu")
SuperTool.print_to_pslf("Negative Step Size:  ", DnStepInPU," pu")


i = Pslf.record_index(1,1,1,2,"1",1, -1)
SuperTool.print_to_pslf("System Impedance:    ", Secdd[i].Zsecx)

if(PSS_On==1):
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