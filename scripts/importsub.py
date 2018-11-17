#!/usr/bin/env python2
import sys
import os

# The script is to import all dependencies of a smart contract into 
# single uber file which can then be deployed via Mist or Ethereump wallet 
# tested and being used in conjunction with  

imported=[]
def importer( fname ):
    "This reads solidity source and substitutes instead of imports their bodies"
    global imported
    with open(fname,"r") as f: #opens file with name of "test.txt"
        for line_long in f:
            line=line_long.rstrip().lstrip()
#            if ( not line.startswith("pragma ") ):
            if ( line.startswith("import ") ):
                fname = line.replace('"', '\'').split("'")[1].lstrip("../").lstrip("./")
                print("// Importing file "+fname)
                found=0
                for p in ["","contracts/","node_modules/","node_modules/openzeppelin-solidity/contracts/token/ERC20/","node_modules/openzeppelin-solidity/contracts/","node_modules/openzeppelin-solidity/contracts/crowdsale/"]:
                    if ( os.path.isfile(p+fname) ):
                        found=1
                        if ( not p+fname in imported ):
                            importer(p+fname)
                            imported.append(p+fname)
                if ( found == 0 ):
                    print("// file not found "+fname)
            else:
                print(line_long.rstrip())
        return

importer(sys.argv[1])

print("// imported "+str(imported))
