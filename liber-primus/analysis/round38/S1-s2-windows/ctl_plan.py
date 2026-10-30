import json,sys
w=int(sys.argv[1]); a=max(0,w-2048); b=a+4096
json.dump([{"lane":"CTL","reducer":"random29","relation":"exact","offset":0,"from":a,"to":b,"cand_bar":5.0,"claim_bar":7.6341931878728095}],open(f'/vercel/w/ctl/plan_{w}.json','w'))
