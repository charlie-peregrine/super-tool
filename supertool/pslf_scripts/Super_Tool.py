from PSLF_PYTHON import *
import csv


###################################################################################################
#   Program: SuperTool.py
# 
#   Ported by: Josiah D. Gibbs
#   Developed On: PSLF V23.2.6 / Python 3.6.8
# 
#   Revisions:
#   -10/11/2023 convert from epcl to python - Phase 1
#   -11/03/2023 Phase 2
# 
#   Description:
#   -This class defines the functions used in the SuperTool class, imported into all the python scripts.
# 
###################################################################################################

# custom exception for supertool errors
class SuperToolFatalError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SuperTool:
    def __init__():
        return    
    
    def print_to_pslf(*strings):
        # creates a compact print function that prints to pslf console
        output = ""
        for word in strings:
            output += str(word)
        output += "\n"
        Pslf.print_to_pslf(output)
        return
    
    
    @staticmethod
    def fatal_error(message):
        # prints error message to pslf console and terminal window
        string1 = "Error: "
        string2 = "\nExitting python simulation..."
        message = string1+message+string2
        print(message)
        SuperTool.print_to_pslf(message)
        raise SuperToolFatalError(message)


    @staticmethod
    def pwd():
        # print working directory and project directory
        project_directory = os.path.dirname(os.path.realpath(__file__))
        SuperTool.print_to_pslf("\nProject directory: ",project_directory)
        print("project directory: ",project_directory)
        os.chdir(project_directory)
        print("working directory: ", os.getcwd())
        return
    

    @staticmethod
    def launch_Pslf(project_directory, silent=False):
        # launches pslf gui      
        os.chdir(project_directory) # changes the python working directory to the project directory
        # Initializes the PSLF instance
        try:
            init_pslf(use_existing=True, working_directory=project_directory, silent = silent) 
            print("GUI already launched")
        except:
            init_pslf(use_existing=False, working_directory=project_directory, silent = silent) 
            print("launching GUI")
        finally:
            pass
        return
    

    @staticmethod
    def psds():
        # clears the pslf dynamic memory
        ret = Pslf.clear_dyn_memory()
        return ret

    
    @staticmethod
    def getf(sav_filename):
        # loads a sav file into pslf
        Pslf.print_to_pslf("getf()\n")
        try: 
            ret = Pslf.load_case(sav_filename)  
            if(ret!=0): 
                SuperTool.fatal_error(".sav case not loaded!")
        except:
            SuperTool.fatal_error(".sav file not found!")
            exit()
        return ret
    

    @staticmethod
    def setf(Pgen,Qgen,MVAbase,Vgen,Vbase,Zbranch,set_flow,sav_flow,sav_name):
        Pslf.print_to_pslf("setf()\n")
        Generator[0].Mbase = MVAbase # sets generator mva base
        if (set_flow == TRUE):
            SuperTool.set_loadflow_parameters(Pgen,Qgen,Vgen/Vbase,Vbase,Zbranch)

        if (sav_flow == TRUE):
            sure = input("Are you sure you want to save this loadflow? This will override existing .sav file. (y/n): ")
            if sure == "y":
                Pslf.save_case(sav_name)
    

    @staticmethod
    def soln(option):
        # attempts to solve the loadflow
        Pslf.print_to_pslf("soln()\n")
        ret = Pslf.solve_case(option)                                              
        if(ret!=0):
            SuperTool.fatal_error("Could not solve .sav case!")
        return ret
    
    
    @staticmethod
    def rdyd(file, report, setup_flag, sort_flag, read_mva_flag):
        # rdyd() equivalent - attempts to read dyd file
        Pslf.print_to_pslf("rdyd()")
        ret = Pslf.load_dyd(file, report, setup_flag, sort_flag, read_mva_flag)                
        if(ret!=0):
            SuperTool.fatal_error("Could not load dyd file.")
        return ret
    
    
    @staticmethod
    def init(channel_file, init_report_file, fix_bad_data, turn_off_unused_models, in_run_epcl, violation_criteria_file, load_net):
        # init() equivalent
        Pslf.print_to_pslf("init()")
        ret = Pslf.init_dyn(channel_file, init_report_file, fix_bad_data, turn_off_unused_models, in_run_epcl, violation_criteria_file, load_net)
        if(ret!=0):
            SuperTool.fatal_error("Could not initialize dyd file.")
        return ret

    
    @staticmethod
    def turn_off_pss(dp):
        # turns off pss model in the .dyd. Argument is dp = DynamicsParameters()
        for i in range(dp.Nmodels):
            min = Model[i].ModLibNo
            if(ModelLibrary[min].Type == "s"):              # searches for pss models 
                Model[i].St = 0                             # sets status of the pss model to disabled.
        return


    @staticmethod
    def set_gens_ID(dp):
    # this function is not yet working. I want it to read the ID of the generators in the
    # dyd file and compare it to the ID of the generators in the sav, and then return 
    # false if these IDs dont match.
        print("In set_gens_ID()")
        # turns off pss model in the .dyd. Argument is dp = DynamicsParameters()
        gensIndex=0                                     # sets up variable to count number of gens
        for i in range(dp.Nmodels):
            print("gensIndex: ",gensIndex)
            min = Model[i].ModLibNo
            if(ModelLibrary[min].Type == "g"):          # searches for gens models 
                
                print("Generator[",gensIndex,"]:.Id ", Generator[gensIndex].Id)
                print("Model[",i,"].Id: ", Model[i].Id)
                Generator[gensIndex].Id = Model[i].Id   # sets gens ID to the dyd ID
                gensIndex+=1
        return

    @staticmethod
    def chf_to_csv(csv_filename):
        # converts chf to csv
        ret = Pslf.channel_to_csv(True, False, "", csv_filename)
        if(ret<0):
            errmsg = "Error: could not create .csv file."
            SuperTool.print_to_pslf(errmsg)
            print(errmsg)
        return ret
    

    @staticmethod
    def set_loadflow_parameters(Pgen,Qgen,Vgen,Vbase,Zbranch):
        # sets/solves the .save case P, Q, V, Zbranch parameters
        SuperTool.print_to_pslf("set_loadflow_parameters()")
        # This sets the nominal bus voltage and impedance
        Bus[0].Basekv = Vbase               # sets the generator bus
        Bus[1].Basekv = Vbase               # sets the system bus
        Secdd[0].Zsecx = Zbranch            # sets the branch positive sequence reactance

        # This sets the generator bus P/Q
        Generator[0].Pgen = Pgen
        Generator[0].Qmax = Qgen
        Generator[0].Qmin = Qgen
            
       
        ret = SuperTool.adjust_bus_kV(Vgen)  # this sets the generator bus voltage
        if (ret!= 0):
            errmsg = "Couldn't solve bus voltage"
            SuperTool.fatal_error(errmsg)
        return


    @staticmethod
    def adjust_bus_kV(vTarget):
        # Adjusts scheduled voltage and solve until bus voltage matches target voltage 
        # returns 0 if success, -1 if failure
        
        iteration = 0
        SuperTool.print_to_pslf("adjust_bus_kV()")            
        vSchedule = vTarget                 # first, guess the required bus voltage
        vTolerance = 0.00005                 # set up other stuff
        vDelta = 0.01  
        max_iterations = 35 
        while(TRUE):                        # run while loop to solve voltage
            iteration+=1
            Bus[1].Vsched = vSchedule
            ret = SuperTool.soln(0)          # solves the sav case at this voltage
            vSim = Bus[0].Vm                # sets simulation voltage from the solved bus voltage magnitude loadflow          
            vError = abs(vSim - vTarget)    # then, calculate how much our simulation is off by
            if(vError<vTolerance):          # if the voltage error is within our target, then break while this loop
                return 0                    # success
            elif(iteration>max_iterations):               # if more than 20 iterations are used, V cannot be not solved
                return -1                   # failure

            SuperTool.print_to_pslf("Adjusting bus kV...")                
            if(vSim<vTarget):               # if simulation voltage is larger than target voltage, increase the scheduled voltage and reduce the delta
                if(vDelta<0.0):
                    vDelta = vDelta * -0.5
            elif(vSim>vTarget):             # otherwise, decrease the scheduled voltage and reduce the delta
                if(vDelta>0.0):
                    vDelta = vDelta * -0.5
            vSchedule = vSchedule + vDelta
        return
    

    @staticmethod
    def construct_default_loadflow(sav_filename):
        # future function - builds the loadflow 

        # add GENERATOR Bus
        # add SYSTEM Bus
        # Add Branch
        # Add Generator
        Pslf.save_case(sav_filename) # Creates new sav case 

        return

