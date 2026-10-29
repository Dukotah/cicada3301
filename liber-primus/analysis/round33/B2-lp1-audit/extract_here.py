import os,sys
sys.dont_write_bytecode=True
T1=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','round19','T1'))
sys.path.insert(0,T1)
import t1_extract as E
import t1_reader as T0; T0.VENDOR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"vendor_fetch")
E.WORK=os.path.join(os.path.dirname(os.path.abspath(__file__)),'work'); os.makedirs(E.WORK,exist_ok=True)
face=sys.argv[1]; pages=range(int(sys.argv[2]),int(sys.argv[3])+1)
E.extract(face,list(pages))
