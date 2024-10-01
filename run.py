import os
import argparse
import pathlib
import sys
import subprocess
import traceback

def mkdir(path): 
	if not os.path.exists(path):
		os.makedirs(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start App Exploration')
    parser.add_argument('package', metavar='P', type=str, nargs=1,
                    help='package name')
    
    app = parser.parse_args().package[0]


    current_dir = os.getcwd()
    APKS_DIR = os.path.join(current_dir,"apks")
    Output_DIR = os.path.join(current_dir,"res",app)
    mkdir(Output_DIR)

    Network_script = os.path.join(current_dir,"network","networkflow.py")
    Network_script_new = os.path.join(Output_DIR,"networkflow_"+app+".py")
    Network_output = os.path.join(Output_DIR,"network.json")
    Network_Log = os.path.join(Output_DIR,"network_log.txt")
    pathlib.Path(Network_output).touch()

    sed_cmd = ["sed","18s!+++++!"+Network_output+"!",Network_script]
    mitmdump_cmd = ["mitmdump", "-s", Network_script_new]

    Hook_output = os.path.join(Output_DIR,"hook.xls")
    Hook_cmd = "python3 hook/camille.py " + app + " -es hook/script_encrypt.js -npp -f " + Hook_output
    Hook_Log = os.path.join(Output_DIR,"hook_log.txt")
    pathlib.Path(Hook_output).touch()
	
    try:
        subprocess.run(["adb","install",os.path.join(APKS_DIR,app+".apk")])
        subprocess.run(["adb","shell","am kill-all"])
        print("App installed")

        fd1 = os.open(Network_script_new, os.O_RDWR | os.O_CREAT)
        fd2 = os.open(Network_Log, os.O_RDWR | os.O_CREAT)
        fd3 = os.open(Hook_Log, os.O_RDWR | os.O_CREAT)
        subprocess.run(sed_cmd, stdout=fd1)
        os.close(fd1)
        print("generate mitm script")
        proc1 = subprocess.Popen(mitmdump_cmd, stdout=fd2)
        print("mitm started")
        
        proc2 = subprocess.Popen(Hook_cmd.split(), stdout=fd3)
        print("Hook started")

        message = input("终止时请输入任意字符：")
        if message:
            proc2.terminate()
            proc2.wait()
            proc1.terminate()
            proc1.wait()
            os.close(fd2)
            os.close(fd3)
    except Exception as e:
        print(e)
	

    
