import re,sys
s=open('/vercel/w/in/grind27.c').read()
old='''        if (self_test(NULL)) { printf("ABORT: self-test failed; broken scan, not a null\n"); return 1; }
        return run_plan(plan, seconds);'''
new='''        if (self_test(NULL)) { printf("ABORT: self-test failed; broken scan, not a null\n"); return 1; }
        { const char *cc = getenv("GRIND27_CTL_CIPHER");   /* R38 control-only: swap C_SCREEN AFTER the real self-test */
          if (cc) { load_cipher_override(cc, C_SCREEN); printf("CTL: C_SCREEN replaced from %s\n", cc); } }
        return run_plan(plan, seconds);'''
assert s.count(old)==1
open('/vercel/w/ctl/grind27_ctl.c','w').write(s.replace(old,new))
