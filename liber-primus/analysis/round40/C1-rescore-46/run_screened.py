"""python run_screened.py <stage>   stages: r30 | c18 | r43 | r32 | r33 | r47   (control first, then run; resumable)"""
import os, sys, json, time, random
from c1common import *
import engine as E
import keysets as KS
os.makedirs(F("controls"), exist_ok=True)
MD = deg_thr(); MDSIOC = (MD[0], MD[1])

def do_control(fam, ks):
    p = F("controls", fam + ".json")
    if os.path.exists(p): return json.load(open(p))
    c = E.control_screened(fam, ks); json.dump(c, open(p, "w"), indent=1); return c

def stage_r30():
    ents, na, nn = KS.vig_entries(); ks = KS.vig_keyset(ents); fam = "R30_B1_artifact_keys"
    c = do_control(fam, ks)
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED -> inconclusive"); return
    Cs = KS.page_Cs(120, True)
    E.run_screened(fam, ks, Cs, "R30 B1: %d curated alpha keys (b1_keys.build, 43 auto-extracted keys unavailable: raw archive not committed) + 16 numeric streams x {digit,pair29}, <=12 phases, sign +-1, atbash 0/1, page-start L=120 head of every page >= 120 runes" % na,
                   "pf_v4_12 head screen -> beam_v3 keyskip1+2 panel-R36", MDSIOC)

def stage_c18():
    ks = KS.vig_keyset(KS.c18_entries()); fam = "C18_numeric_PS_tweet_mayan"
    c = do_control(fam, ks)
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED -> inconclusive"); return
    E.run_screened(fam, ks, KS.page_Cs(120, True), "R10b/c18 numeric: P.S. digit string + @1231507051321 handle (single/pairs/disjoint pairs/reversed) + Mayan list, ALL phases, sign +-1, atbash 0/1, page-start L=120",
                   "pf_v4_12 head screen -> beam_v3 keyskip1+2 panel-R36", MDSIOC)

def stage_r43():
    ks, nw = KS.b5_keyset(64); fam = "R43_B5_composed_keys"
    c = do_control(fam, ks)
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED -> inconclusive"); return
    Cs = KS.page_Cs(120, False, pages={0, 1, 2, 5, 20})
    E.run_screened(fam, ks, Cs, "R43 B5 composed keys K=cw*W[(j+wp)]+cg*G[j+go]: %d words x 3 generators (phi_prime, prime, totient) x 8 coefficient pairs x all wphases x goff 0..63 = 289,344 configs; pages 0,1,2,5,20 at L=120 (page 54 has 76 runes < 120: not covered), sign +1 (coefficient pairs cover -1)" % nw,
                   "pf_v4_12 head screen -> beam_v3 keyskip1+2 panel-R36", MDSIOC)

def stage_r32():
    ks, ns, nsym = KS.b04_keyset(("slogan",)); fam = "R32_B04_slogan_seeds"
    c = do_control(fam, ks)
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED -> inconclusive"); return
    E.run_screened(fam, ks, KS.page_Cs(120, True), "R32 B04 SLOGAN seeds (%d text forms) x 16 generators x 5 reductions x dir fwd/rev x sign +-1, nsym=%d, stage A (page-0 head) + stage C (per-page key restart) at L=120 over every page >= 120 runes, atbash 0/1" % (ns, nsym),
                   "pf_v4_12 head screen -> beam_v3 keyskip1+2 panel-R36", MDSIOC)

def stage_r32lp():
    ks, ns, nsym = KS.b04_keyset(("lp",)); fam = "R32_B04_lp_seeds_stageA"
    c = do_control(fam, ks)
    if not c["gate_ge4_of_6_per_relation"]: log(fam, "CONTROL FAILED -> inconclusive"); return
    Cs = [("p00", list(U[:120])), ("p00_atb", [(28 - c_) % 29 for c_ in U[:120]])]
    E.run_screened(fam, ks, Cs, "R32 B04 LP-line/word seeds (%d seed byte-strings, label prefix lp) x 16 generators x 5 reductions x dir x sign, stage A only (LP2 head L=120, atbash 0/1)" % ns,
                   "pf_v4_12 head screen -> beam_v3 keyskip1+2 panel-R36", MDSIOC)

if __name__ == "__main__":
    globals()["stage_" + sys.argv[1]]()
