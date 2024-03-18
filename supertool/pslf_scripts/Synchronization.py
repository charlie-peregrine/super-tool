from PSLF_PYTHON import *
from supertool.pslf_scripts.Super_Tool import *


###################################################################################################
#   Program: Synchronization.py
# 
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
# 
#  Description:
#  -This function uses the built in python code to run the scipt portion, and a syncmod.p epcl as 
#   the user written model, since to date there is no python support for epcmod() user written 
#   models. 
# 
###################################################################################################

def run(test, no_gui=False):

    #--------------------------------------------------------------------------------------------------
    # Configure for your test with the following parameters
    #--------------------------------------------------------------------------------------------------

    # input files
    dyd_filename      = test.attrs["dyd_filename"].get()      # "U2_SYNC.dyd"
    sav_filename      = test.attrs["sav_filename"].get()      # "U2_SYNC.sav"

    # output files
    chf_filename      = test.attrs["chf_filename"].get()      # "U2_SYNC_sim.chf"
    csv_filename      = test.attrs["csv_filename"].get()      # "U2_SYNC_sim.csv"
    syncmod_filename  = test.attrs["syncmod_filename"].get()  # "syncmod.p"     # This parameter should have this default filename
    rep_filename      = test.attrs["rep_filename"].get()      # "rep.rep"

    GenModelName     = test.attrs["GenModelName"].get()     # "genqec"

    SyncTimeInSecs   = test.attrs["SyncTimeInSecs"].get()   # 0.983
    TotTimeInSec     = test.attrs["TotTimeInSec"].get()     # 5.00
    PreSyncHz        = test.attrs["PreSyncHz"].get()        # 59.992
    PostSyncHz       = test.attrs["PostSyncHz"].get()       # 59.979
    BaseHz           = test.attrs["BaseHz"].get()           # 60.0
    SyncAngleDegs    = test.attrs["SyncAngleDegs"].get()    # -2.5
    PSS_On           = test.attrs["PSS_On"].get()           # False
    AVR_On           = test.attrs["AVR_On"].get()           # True        # T/F
    ChangePref       = test.attrs["ChangePref"].get()       # True        # T/F
    OnlinePref       = test.attrs["OnlinePref"].get()       # 1.002       # if changePref, then this is used
    PrefDelay        = test.attrs["PrefDelay"].get()        # 0.000       # if changePref, then this is used
    ChangeVref       = test.attrs["ChangeVref"].get()       # True        # T/F
    OnlineVref       = test.attrs["OnlineVref"].get()       # 1.0255      # if changeVref, then this is use

    #----------------------------------
    # loadflow Parameters
    #----------------------------------

    # GenBus (aka presync voltage)
    GenVinit         = test.attrs["GenVinit"].get()         # 12.763   # kV  # changes genbus voltage
    GenVbase         = test.attrs["GenVbase"].get()         # 12.47
    Zbranch          = test.attrs["Zbranch"].get()          # 0.2      # pu

    # SMIB (aka postsync voltage)
    SmibVinit        = test.attrs["SmibVinit"].get()        # 12.7705  # kV  # changes system bus voltage
    SmibVbase        = test.attrs["SmibVbase"].get()        # 12.47


    #--------------------------------------------------------------------------------------------------

    ## dont change These parameters. this handles to the backend epcl user written model. 
    SubGenModName       = "sub.GenModelName"
    Syncmod_src         = __file__.rsplit('\\', maxsplit=1)[0] + '\\' + "syncmod_src.txt" # "syncmod_src.txt"

    project_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(project_directory)


    ## reads the source syncmod.p file and copies it to an output file, with certain strings text replaced.
    with open(syncmod_filename, 'w') as out:
        with open(Syncmod_src, 'r') as f:
            count=0
            lines = f.readlines()
            for line in lines:
                count+=1
                line=re.sub(SubGenModName,GenModelName,line)
                print("line", count,":",line,end='',flush=True)
                out.write(line)



    SuperTool.launch_Pslf(project_directory, silent=no_gui)
    SuperTool.pwd()

    ##------------------------------------------------##
    ## Do some pre-simulation calculations and checks ##
    ##------------------------------------------------##

    # global variable initialization
    DelayedPref=0
    InitialSpeed=0


    if (ChangePref==1) and (PrefDelay>0.001):
        DelayedPref=1
    else:
        DelayedPref=0

    if ChangePref==1:
        SuperTool.print_to_pslf("in if(changePref==1)")
        if (SyncTimeInSecs + PrefDelay) >= TotTimeInSec:
            SuperTool.print_to_pslf("!!! Changing the Total Simulation time you specified")
            TotTimeInSec = SyncTimeInSecs + PrefDelay + 1

    InitialSpeed = 1.0 - (PostSyncHz - PreSyncHz) / BaseHz


    ## Put the 'InitialSpeed' in a mailbox so synchmod can access it
    # Mailbox[0].Number[2] = InitialSpeed

    mailbox = Mailbox()
    mailbox.set_number_at(2,InitialSpeed)

    SuperTool.print_to_pslf("\n--- Starting Synchronization Test Simulation ---")



    ##-------------------##
    ## Load the SAV Case ##
    ##-------------------##
    SuperTool.getf(sav_filename)


    # Set the syncronization angle requested by the user # 
    SyncAngleRads = SyncAngleDegs * 3.1415 / 180
    Bus[1].Va = SyncAngleRads

    # Set the generator bus voltage requested by the user #
    Bus[1].Basekv = GenVbase
    Bus[1].Vsched = GenVinit/GenVbase
    
    # Set the system bus voltage requested by the user #
    Bus[0].Basekv = SmibVbase
    Bus[0].Vsched = SmibVinit/SmibVbase
    
    # Start the simulation with the high Z branch enabled #
    Secdd[0].St = 0
    Secdd[1].St = 1

    # Set the impedance of the branch that will be enabled when we sync #
    Secdd[0].Zsecx = Zbranch

    SuperTool.soln(0)

    ##-----------------------------------------##
    ## Solve, Load and initialize the DYD file ##
    ##-----------------------------------------##

    SuperTool.psds()       
    SuperTool.rdyd(dyd_filename, rep_filename,1,0,1)
    SuperTool.init(chf_filename, rep_filename,0,1,"","", 1)

    ##------------------------------------------------------##
    ## Turn off the PSS if it isn't used in this simulation ##
    ##------------------------------------------------------##

    dp = DynamicsParameters()                               # gets all the dynamics parameers
    if(PSS_On==0):
        SuperTool.turn_off_pss(dp)

    ##------------------------------------------------------##
    ## Turn off the AVR if it isn't used in this simulation ##
    ##------------------------------------------------------##
    if not AVR_On:
        for i in range(dp.Nmodels):
            min = Model[i].ModLibNo
            if(ModelLibrary[min].Type == "x"):              # searches for exciter models 
                Model[i].St = 0                             # sets status of the exciter model to disabled.
                Pslf.print_to_pslf("AVR OFF\n")



    ##----------------------------------------------------##
    ## Run the pre-synchronization part of the simulation ##
    ##----------------------------------------------------##


    dp.Delt = 0.001
    dp.Conv_Mon = 0                     # set to 1 to display convergence monitor
    dp.Nplot = 1                        # save data every cycle
    dp.Nscreen = 100                    # display values on screen every 0.5 second
    dp.Tpause = SyncTimeInSecs          # pauses after this amount of time
    i = Pslf.run_dyn()



    ##---------------------------------##
    ## Prepare for the synchronization ##
    ##---------------------------------##

    # Switch to the lower impedance bus #   
    Secdd[0].St = 1
    Secdd[1].St = 0
    dp.New_Fact = 1
    
    if(ChangeVref==1):
        nMod = Pslf.model_index(1,GenModelName,1,-1,"1 ",1,-1)
        k = Model[nMod].K
        SuperTool.print_to_pslf("--- Changing Vref from ", GeneratorInitialConditions[k].Vref  , " to " , OnlineVref )     
        GeneratorInitialConditions[k].Vref = OnlineVref



    # Signal our epcmod that we want to sync now #
    mailbox.set_number_at(1,1.0)

    if DelayedPref < 0.001:
        if ChangePref==1:
            nMod = Pslf.model_index(1,GenModelName, 1,-1,"1",1,-1)
            k = Model[nMod].K
            SuperTool.print_to_pslf("--- Changing Pref from ", GeneratorInitialConditions[k].Pref , " to " , OnlinePref)
            GeneratorInitialConditions[k].Pref = OnlinePref

        SuperTool.print_to_pslf("--- Closing the Breaker")
        dp.Nplot = 1
        dp.Nscreen = 2000
        dp.Tpause = TotTimeInSec
        i = Pslf.run_dyn()
        i = Pslf.end_dyn_run()
        i = SuperTool.chf_to_csv(chf_filename,csv_filename)

    else:
        SuperTool.print_to_pslf("--- Closing the Breaker")
        dp.Nplot = 1
        dp.Nscreen = 2000
        dp.Tpause = SyncTimeInSecs + PrefDelay
        i = Pslf.run_dyn()

        nMod = Pslf.model_index(1,GenModelName,1,-1,"1 ",1,-1)
        k = Model[nMod].k
        SuperTool.print_to_pslf("--- Changing Pref from ", GeneratorInitialConditions[k].Pref , " to " , OnlinePref)
        GeneratorInitialConditions[k].Pref = OnlinePref

        SuperTool.print_to_pslf("--- Completing the simulation with new Pref")
        dp.Nplot = 1
        dp.Nscreen = 2000
        dp.Tpause = TotTimeInSec
        i = Pslf.run_dyn()
        i = Pslf.end_dyn_run()
        i = SuperTool.chf_to_csv(chf_filename,csv_filename)

    ##----------------------------------------------##
    ## Remind the user what settings were just used ##
    ##----------------------------------------------##
        
    i = Pslf.record_index(1,1,1,2,"1",1, -1)
    X = Secdd[i].Zsecx

    SuperTool.print_to_pslf("<<<<----------------------------------------------------")
    SuperTool.print_to_pslf("Previous Synchronization Simulation Used:")
    SuperTool.print_to_pslf("   System Impedance:    ",  X)
    if PSS_On:
        SuperTool.print_to_pslf("   PSS Status:             On")
    else:
        SuperTool.print_to_pslf("   PSS Status:             Off")

    SuperTool.print_to_pslf( "   Sync angle:          " , SyncAngleDegs)
    SuperTool.print_to_pslf( "   Pre-Sync Speed       " , PreSyncHz)
    SuperTool.print_to_pslf( "   Post-Sync Speed      " , PostSyncHz)
    SuperTool.print_to_pslf( "   Initial Speed        " , InitialSpeed)
    SuperTool.print_to_pslf( "   Dyd File Name:       " , dyd_filename)
    SuperTool.print_to_pslf( "   Chf File Name:       " , chf_filename)
    SuperTool.print_to_pslf( "   Csv File Name:       " , csv_filename)
    SuperTool.print_to_pslf( "   Syncmod File Name:   " , syncmod_filename)

    if ChangeVref == 1:
        SuperTool.print_to_pslf( "* After sync, changed Vref to " , OnlineVref)
    if ChangePref == 1:
        SuperTool.print_to_pslf( "* ", PrefDelay, " seconds after sync, changed Pref to " , OnlinePref)

    SuperTool.print_to_pslf( "----------------------------------------------------\n\n\n")

    print("Finished running Synchronization.py script!")

