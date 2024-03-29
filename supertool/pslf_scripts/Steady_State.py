from PSLF_PYTHON import *
from supertool.pslf_scripts.Super_Tool import *
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


def run(test, no_gui=False):

    #--------------------------------------------------------------------------------------------------
    # Configure for your test with the following parameters
    #--------------------------------------------------------------------------------------------------
    
    # @TODO savecasefiles used? UseGenField is a bool?
        # test.attrs["dyd_filename"].var.get()
    dyd_filename        = test.attrs["dyd_filename"].get()       # "HCPR1.dyd"
    sav_filename        = test.attrs["sav_filename"].get()       # "HCPR1_LR.sav"
    chf_filename        = test.attrs["chf_filename"].get()       # "HCPR1_LR_new_sim.chf"
    rep_filename        = test.attrs["rep_filename"].get()       # "Rep.rep"
    in_filename         = test.attrs["in_filename"].get()        # "HCPR1_LR_IN.csv"
    out_filename        = test.attrs["out_filename"].get()       # "HCPR1_LR_OUT_new.csv"
    # out_casename        = test.attrs["out_casename"].get()       # "HCPR1_LR.txt"
    if_base             = test.attrs["if_base"].get()            # 740
    if_res              = test.attrs["if_res"].get()             # 0.0
    # SaveCaseFiles       = test.attrs["SaveCaseFiles"].get()      # 0 # generally leave as 0
    UseGenField         = test.attrs["UseGenField"].get()        # 0 # set this to '1' if you want to use generator field even for brushless 
    Vbase               = test.attrs["Vbase"].get()
    Zbranch             = test.attrs["Zbranch"].get()
    #mva_base           = test.attrs["mva_base"].get()           # 145.0

    #----------------------------------
    # User Defined Parameters
    # Note that these are not accessed
    # unless decided so by the user
    #----------------------------------

    UserVar1        = test.attrs["UserVar1"].get()
    UserVar2        = test.attrs["UserVar2"].get()
    UserVar3        = test.attrs["UserVar3"].get()
    UserVar4        = test.attrs["UserVar4"].get()
    UserVar5        = test.attrs["UserVar5"].get()


    # 0 initialize 4 variables used later. NOT inputs
    Ifd_A   = 0.0
    
    Ifd_pu  = 0.0
    Efd_pu  = 0.0
    Efe_pu  = 0.0
    Ife_pu  = 0.0
    Ef_pu   = 0.0
    If_pu   = 0.0

    ExcModIndex         = 0


    # gets the project directory of this test and initialize the PSLF instance
    project_directory = test.get_dir().replace("/", "\\") # os.path.dirname(os.path.realpath(__file__))
    SuperTool.launch_Pslf(project_directory, silent=no_gui)

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


    # # Gets the Nominal Generator Bus Voltage and branch impedance from the first two lines of the CSV Input File
    # Vbase = float(csvInData[0][0])
    # Zbranch = float(csvInData[1][0])


    #  This opens the CSV Output File for writing
    csvInFormat = ""
    try:
        f = open(os.path.join(project_directory,out_filename), "w", newline='')
        csvOutFile = csv.writer(f)
        csvHeader = ['Load Point','P (MW)','Q (MVAR)','Vt (kV)','Ef (V)','If (A)','If-sim (pu)','If-meas (pu)', 'Diff (%)', 'Abs(Diff) (%)','','Vt-meas (pu)',
                     'Vt-sim (pu)','BusV-sched (pu)','','Efd-sim','Ifd-sim','Efd=Ifd?','Efe-sim','Ife-sim (pu)','Efe=Ife?',
                     '','If-sim (A)']
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


    print("csvInData: ", csvInData)
    print("length csvInData[0][1:3]: ",len(csvInData[0][1:3]))
    print("length csvInData[1][1:3]: ",len(csvInData[1][1:3]))

    # if the first line is a header line then skip it
    try:
        float(csvInData[0][0])
        csvRowIndex=0
    except ValueError:
        csvRowIndex=1
    
    # if the first 2 lines are set up like it was printed
    # out by the spreadsheet ( first 2 rows 1 element, 3 elements every other row)
    # then act like it works like that @TODO prompt to override?
    if  (csvInData[0][1:3] == [] and csvInData[1][1:3] == []) or \
        (csvInData[0][1:3] == ['',''] and csvInData[1][1:3] == ['','']):
            csvInFormat = "OLD"
            Vbase = float(csvInData[0][0])
            Zbranch = float(csvInData[1][0])
            csvRowIndex=2
            print("csvRowIndex", csvRowIndex)
            SuperTool.print_to_pslf(f"Using Vbase and Zbranch from {in_filename}")
    else:
        csvInFormat = "NEW"
    
    
    print("csvinformat: ", csvInFormat)

    while(TRUE):
        # sets the measured generator quantities from the csv row into local variables
        Pgen  = float(csvInData[csvRowIndex][0])
        Qgen  = float(csvInData[csvRowIndex][1])
        if(csvInFormat=="NEW"):
            Vtgen = float(csvInData[csvRowIndex][2]) / Vbase # per unitize voltage
        else:
            Vtgen = float(csvInData[csvRowIndex][2])
        
        try:
            Efdgen = float(csvInData[csvRowIndex][3])
            Ifdgen = float(csvInData[csvRowIndex][4])
            fields_measured = True
            print("efd and ifd in data")
        except IndexError:
            fields_measured = False
            print("no efd and ifd in data")
            

        SuperTool.print_to_pslf("\nLoad Point #",csvRowIndex-1)
        SuperTool.print_to_pslf("P: ",Pgen," Q: ",Qgen," Vt: ",Vtgen)

        SuperTool.getf(sav_filename)
        SuperTool.rdyd(dyd_filename, rep_filename, 1,0,1)
        
        # This initializes bus parameters for the loadflow
        SuperTool.set_loadflow_parameters(Pgen,Qgen,Vtgen,Vbase,Zbranch)
        ret = SuperTool.init(chf_filename,rep_filename,0,1,"","", 1)

        #  Retrieve Ifd_pu and Efd_pu for writing to output csv file
        # if(UseGenField):

        #initializes the exciter and generator field quantities as if it were static
        Efd_pu  = GeneratorInitialConditions[0].Efd
        Ifd_pu  = GeneratorInitialConditions[0].Ladifd
        Ife_pu  = 0
        Efe_pu  = 0
        Ef_pu   = Efd_pu
        If_pu   = Ifd_pu

        #if it is brushless not static, then the exciter quantities are set
        if('esac' in excModName):
            print("Excitation Type: Brushless")
            Efe_pu  = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vr")
            Ife_pu  = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
            # if UseGenField selected, it uses the generator field for steady state analysis
            if  UseGenField:
                Ef_pu = Efd_pu
                If_pu = Ifd_pu
            else:
                Ef_pu = Efe_pu
                If_pu = Ife_pu

        elif('rexs' in excModName):
            print("Excitation Type: Brushless")
            # note that rexs model exciter field quantities have different names in model than the esac models
            Efe_pu  = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"vfe")
            Ife_pu  = Pslf.get_model_parameters(1,1,-1, "1 ", 1, excModName,"ife")
            # if UseGenField selected, it uses the generator field for steady state analysis
            if  UseGenField:
                Ef_pu = Efd_pu
                If_pu = Ifd_pu
            else:
                Ef_pu = Efe_pu
                If_pu = Ife_pu

        else:
            print("Excitation Type: Static or DC")
            Ifd_pu  = GeneratorInitialConditions[0].Ladifd
            Efd_pu  = GeneratorInitialConditions[0].Efd
            Ife_pu  = 0
            Efe_pu  = 0

        # calculates Exciter Field in amps
        Ifd_A = Ifd_pu * (if_base-if_res)

        #calculates if simulation run is at steady state by comparing If and Ef
        GenFieldSteady = ''
        if Efd_pu==Ifd_pu: field_Error=0
        else: field_Error = ((Efd_pu-Ifd_pu)/Efd_pu)
        if field_Error<0.0001: GenFieldSteady=True
        else: GenFieldSteady=False

        ExcFieldSteady = ''

        if Efe_pu==Ife_pu: field_Error=0
        else: field_Error = ((Efd_pu-Ifd_pu)/Efd_pu)
        if field_Error<0.0001: ExcFieldSteady=True
        else: ExcFieldSteady=False
            
        
        if fields_measured:
            
            # convert measured exciter field to per unit
            If_pu_meas = (Ifdgen + if_res) / if_base
            diff_perc = 100 * (If_pu - If_pu_meas) / If_pu
            abs_diff_perc = 100 * abs(If_pu - If_pu_meas) / If_pu

            # generate row to write
            csvOutData = [csvRowIndex-1, Pgen, Qgen, round(Vtgen*Vbase,2), round(Efdgen,2), 
                        round(Ifdgen,2), round(If_pu,3), round(If_pu_meas,3), str(round(diff_perc,2))+'%',
                        str(round(abs_diff_perc,2))+'%',
                        '', 
                        round(Vtgen,3), round(Bus[0].Vm,3), round(Bus[1].Vsched,3),
                        '',
                        round(Efd_pu,3), round(Ifd_pu,3), GenFieldSteady, round(Efe_pu,3), round(Ife_pu,3), ExcFieldSteady,
                        '', round(Ifd_A,2)]
        else:
            # generate row to write
            csvOutData = [csvRowIndex-1, Pgen, Qgen, round(Vtgen*Vbase,2), '###', 
                        '###', round(If_pu,3), '###','###%','###%',
                        '',
                        round(Vtgen,3), round(Bus[0].Vm,3),round(Bus[1].Vsched,3),
                        '',
                        round(Efd_pu,3), round(Ifd_pu,3), GenFieldSteady, round(Efe_pu,3), round(Ife_pu,3), ExcFieldSteady,
                        '', round(Ifd_A,2)]
        # write to the csv
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

