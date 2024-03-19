from PSLF_PYTHON import *
import csv
import struct
import traceback

import queue
import threading

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

# thread safe queue for sending user interface updates from backend scripts
ScriptQueue = queue.Queue()

# custom exception for supertool errors
class SuperToolFatalError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SuperToolMessage():
    def __init__(self, message_type: str, message: str = ""):
        self.lock = threading.Lock()
        self.type = message_type
        self.text = message
        # return_val is a value that needs to be passed back to the backend
        # script's execution
        self.return_val = None

    # wait is used when the message requires the user to respond to a prompt
    # or something else to be done synchronously
    # after wait is called in one thread, done should be called in another to
    # complete the exchange
    def wait(self):
        # acquire lock, execution in the running thread continues
        self.lock.acquire()
        # acquire lock again, execution pauses until another thread releases
        self.lock.acquire()
        # release lock in this thread, to be ready for another wait if necessary
        self.lock.release()
    
    # done is used when the message requires synchronicity, for responding to
    # prompts and such. only to be called after wait. Ideally this should only
    # every be called inside the ScriptListener's main loop
    def done(self):
        # release lock
        self.lock.release()
    
    # wrapper for lock.locked, to maintain encapsulation and keep naming cohesive 
    def waiting(self):
        return self.lock.locked()
    
    def __repr__(self):
        return f"[t:{self.type}|m:\"{self.text}\"|r:{self.return_val}|L:{self.waiting()}]"

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
        # # print working directory and project directory
        # project_directory = os.path.dirname(os.path.realpath(__file__))
        # SuperTool.print_to_pslf("\nProject directory: ",project_directory)
        # print("project directory: ",project_directory)
        # os.chdir(project_directory)
        
        # print working directory
        print("working directory: ", os.getcwd())
        return
    

    @staticmethod
    def launch_Pslf(project_directory, silent=False):
        # launches pslf gui      
        os.chdir(project_directory) # changes the python working directory to the project directory
        # Initializes the PSLF instance
        try:
            init_pslf(use_existing=True, path="Pslf.exe", working_directory=project_directory, silent = silent) 
            print("GUI already launched")
        except:
            init_pslf(use_existing=False, path="Pslf.exe", working_directory=project_directory, silent = silent) 
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
            message = SuperToolMessage('ynprompt',
                    "Are you sure you want to save this loadflow? This will override the existing .sav file.")
            ScriptQueue.put(message)
            message.wait()
            if message.return_val:
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


    @staticmethod
    def chf_to_csv_pslf(csv_filename):
        # converts chf to csv
        ret = Pslf.channel_to_csv(True, False, "", csv_filename)
        if(ret<0):
            errmsg = "Error: could not create .csv file."
            SuperTool.print_to_pslf(errmsg)
            print(errmsg)
        return ret


    @staticmethod
    def TupleToString(tup):
        str = ''
        for item in tup:
            str = str + item.decode('unicode_escape')
        str = str.strip(' ')
        str = str.strip('\x00')
        return str

    @staticmethod
    def chf_to_csv(chf_filename,csv_filename):
        if not ".chf" in chf_filename:
            print("not a .chf file")
            return 1
        
        debugMode=False     # if True, then it prints to the console the chf details.
        dataMode=False      # if True, then it outputs the data contents to the console.

        with open(chf_filename, mode="rb") as file:
            with open(csv_filename, "w", newline='') as f:
                csvOutFile = csv.writer(f)
        
                majorversion = struct.unpack('<i', file.read(4))[0]
                minorversion = struct.unpack('<i', file.read(4))[0]
                date01       = struct.unpack('<i', file.read(4))[0]
                spare01      = struct.unpack('<i', file.read(4))[0]
                nchannel     = struct.unpack('<i', file.read(4))[0]
                nheadergroup = struct.unpack('<i', file.read(4))[0]
                time01       = struct.unpack('<f', file.read(4))[0]
                time02       = struct.unpack('<f', file.read(4))[0]
                timelabel    = SuperTool.TupleToString(struct.unpack('<33c', file.read(33)))
                
                if debugMode:
                    print("majorversion: ",majorversion)
                    print("minorversion: ",minorversion)
                    print("date01: ",date01)
                    print("spare01: ",spare01)
                    print("nchannel: ",nchannel)
                    print("nheadergroup: ",nheadergroup)
                    print("time01: ",time01)
                    print("time02: ",time02)
                    print("timelabel: ",timelabel)
                ##-----------------------------------------------------##
                yname = [0 for i in range(nchannel+2)]
                yname[0] = "Unknown"
                yname[1] = "Time"
                namelength = 12
                ichannel = 2
                ##-----------------------------------------------------##
                for iheadergroup in range(nheadergroup):
                    busnumber           = struct.unpack('<i', file.read(4))[0]
                    busname             = SuperTool.TupleToString(struct.unpack('<12c', file.read(12)))
                    buskv               = round(struct.unpack('<f', file.read(4))[0],2)
                    id                  = SuperTool.TupleToString(struct.unpack('<2c', file.read(2)))
                    ck                  = SuperTool.TupleToString(struct.unpack('<2c', file.read(2)))
                    section             = struct.unpack('<i', file.read(4))[0]
                    area                = struct.unpack('<i', file.read(4))[0]
                    zone                = struct.unpack('<i', file.read(4))[0]
                    selnumber           = struct.unpack('<i', file.read(4))[0]
                    modelname           = SuperTool.TupleToString(struct.unpack('<8c', file.read(8)))
                    nchannelperheader   = struct.unpack('<i', file.read(4))[0]
                    unknown40           = struct.unpack('<40c', file.read(40))

                    if debugMode:
                        print("\nloop ", iheadergroup)
                        print("busnumber: ",busnumber)
                        print("busname: ",busname)
                        print("buskv: ",buskv)
                        print("id: ",id)
                        print("ck: ",ck)
                        print("section: ",section)
                        print("area: ",area)
                        print("zone: ",zone)
                        print("selnumber: ",selnumber)
                        print("modelname: ",modelname)
                        print("nchannelperheader: ",nchannelperheader)
                        #print("unknown40: ",unknown40)

                    for ichannelperheader in range(nchannelperheader):
                        tobus      = struct.unpack('<i', file.read(4))[0]
                        toname     = SuperTool.TupleToString(struct.unpack('<12c', file.read(12)))
                        tokv       = round(struct.unpack('<f', file.read(4))[0],2)
                        variable   = SuperTool.TupleToString(struct.unpack('<4c', file.read(4)))
                        cmin       = round(struct.unpack('<f', file.read(4))[0],2)
                        cmax       = round(struct.unpack('<f', file.read(4))[0],2)
                        header     = variable + '-'+ modelname+'-Bus('+str(busnumber)+')'
                        yname[ichannel] = header
                        ichannel+=1

                        if debugMode:
                            print("tobus: ", tobus)
                            print("toname: ", toname)
                            print("tokv: ", tokv)
                            print("variable: ", variable)
                            print("cmin: ", cmin)
                            print("cmax: ", cmax)
                            print("ichannel: ",ichannel)
                            print("ichannelperheader: ", ichannelperheader)
                            print("-----")
                
                if debugMode: print("yname: ",yname)
                csvOutFile.writerow(yname)

                ##-----------------------------------------------------## 
                titletext     = SuperTool.TupleToString(struct.unpack('<400c', file.read(400)))
                comments      = SuperTool.TupleToString(struct.unpack('<1200c', file.read(1200)))
                for itmp in range(100):
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpinteger = struct.unpack('<i', file.read(4))
                    tmpchar    = struct.unpack('<32B', file.read(32))
                for itmp in range(10):
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpfloat   = struct.unpack('<f', file.read(4))
                    tmpinteger = struct.unpack('<i', file.read(4))
                for itmp in range(13):
                    tmpfloat   = struct.unpack('<f', file.read(4))
                ##-----------------------------------------------------##
                eof=False
                error=False
                while not (eof or error):  
                    for i in range(nchannel+2):  
                        try:
                            yname[i] = str(round(struct.unpack('<f', file.read(4))[0],5))
                        except struct.error as err:
                            eof=True
                            break
                        except Exception as err:
                            traceback.print_exception(err)
                            break

                    if dataMode: print("yname",yname)
                    csvOutFile.writerow(yname)
        return
