import re
# parse relikd tokens with their indices to find agreed 'l' and 'I' and 'i' references
lines=[]
grab=False
toks_all=[]
import subprocess
# reuse canonicalize extraction
import os,sys
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/pp49_51')
