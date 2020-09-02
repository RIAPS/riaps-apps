'''
Created on Feb 19, 2017

@author: grunner
'''
import sys
import argparse
import traceback

from gla.agent import Agent


theAgent = None
conf = None
####################

def main(debug=True):
    parser = argparse.ArgumentParser(description="Gridlab-D agent")
    parser.add_argument("name",help="base name for .glm, .gll, .yaml files")
    args = parser.parse_args()
    
    global theAgent
    try:
        theAgent = Agent(args.name)
        theAgent.start()       
        theAgent.run()       
        theAgent.stop()
    except Exception:
        traceback.print_exc()
        if theAgent != None: theAgent.stop()
    #print ("Unexpected error:", sys.exc_info()[0])
    sys.exit()
    
if __name__ == '__main__':
    main()