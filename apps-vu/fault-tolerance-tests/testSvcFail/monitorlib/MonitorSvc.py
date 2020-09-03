import psutil
import time
import os

def main():
    while(1):
        found = False
        for proc in psutil.process_iter():
            if proc.name() == sys.argv[1]:
                print("process name = %s, id = %s, status = %s" % (proc.name, str(proc.pid), proc.status()))
                found = True
        if not found:
            print("service not running!")
                
        time.sleep(1)
 
if __name__ == '__main__':
    main()       