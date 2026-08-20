import os, urllib.parse
onions = """ky2khlqdf7qdznac ut3qtzbrvs7dtvzp auqgnxjtvdbll3pv fv7lyucmeozzd5j4 avowyfgl5lkzfj3n
cu343l33nqaekrnw sq6wmgv2zcsrix6t q4utgdi2n4m4uim5 xsxnaksict6egxkq p7amjopgric7dfdi
pklmx2eeh6fjt7zf emiwp4muu2ktwknf dxwd42hgpd7qrccm gy3hoy2zizvuzvdb gbyh7znm6c7ezsmr
rjzdqt4z3z3xo73h 5fpp2orjc2ejd2g7 5qcyeerbnina7esx y2wyuvrqraowagc5 cginiziglyaobyph
a6d7f6hjfg6eyrye 4l6uipnstbggwjyv wzwmcwmsk5cb7gjn vj7suk6t5bfjugdv qw7mhchzvuq6f2mf
erwfcsdvx6pm2rsk bljflz7gy23uv73l 2lol7ha4j442rqeg yniir5c6cmuwslfl n5gvslqnb4yomt6q
lwplxqzvmgu43uff dbwkwbdidiwbwfau bah37war75xzkpla""".split()

rows = []
def add(tid, url, mt, label):
    rows.append((tid, url, mt, label))

# A. core domains
core = [
 ("845145127.com","domain","2012 countdown site"),
 ("cicada3301.boards.net","domain","community board"),
 ("uncovering-cicada.wikia.com","domain","wikia (old)"),
 ("uncovering-cicada.fandom.com","domain","fandom (new)"),
 ("opensource.exposed","domain","opensource.exposed tools"),
 ("clevcode.org/cicada-3301/","prefix","clevcode writeup"),
 ("reddit.com/r/a2e7j6ic78h0j","prefix","2012 subreddit"),
 ("www.reddit.com/r/a2e7j6ic78h0j","prefix","2012 subreddit www"),
 ("pastebin.com/yEiTHhvF","exact","2017-04-04 signed msg"),
 ("pastebin.com/raw/yEiTHhvF","exact","2017 signed msg raw"),
 ("reddit.com/r/cicada","prefix","r/cicada"),
 ("connortumbleson.com/2019/09/30/the-cicada-3301-mystery/","exact","tumbleson p1"),
 ("connortumbleson.com/2021/01/25/the-cicada-3301-mystery-puzzle-2/","exact","tumbleson p2"),
 ("en.wikipedia.org/wiki/Cicada_3301","exact","wikipedia"),
 ("iamamiwhoami.com","domain","iamamiwhoami (adjacent ARG)"),
 ("3301.onion","domain","3301.onion literal"),
 ("cicada3301.org","domain","copycat/related"),
 ("cicada3301.com","domain","copycat/related"),
 ("cicada3301.net","domain","copycat/related"),
 ("thecicadamystery.com","domain","copycat check"),
 ("isitcicada.com","domain","isitcicada"),
 ("3301.chat","domain","3301 chat"),
 ("cicadasolvers.com","domain","cicadasolvers"),
 ("liberprimus.com","domain","liberprimus"),
 ("rollingstone.com/culture/culture-news/cicada-solving-the-webs-deepest-mystery-84394/","exact","rolling stone"),
 ("grantland.com/hollywood-prospectus/a-wild-bug-chase-cracking-cicada-3301-the-internets-biggest-puzzle/","exact","grantland"),
 ("theregister.com/2014/01/11/cicada_3301_2014/","exact","the register"),
 ("fastcompany.com/3025785/meet-the-man-who-solved-the-mysterious-cicada-3301-puzzle","exact","fastcompany"),
 ("soundcloud.com/nimww/cicada-3301-the-instar-emergence","exact","instar soundcloud"),
 ("archive.4plebs.org/x/thread/18951995/","exact","4plebs thread"),
 ("archive.4plebs.org/x/thread/18491379/","exact","4plebs thread 18491379"),
]
for u,mt,lab in core:
    tid = u.replace("/","_").replace(":","").replace("?","_")
    add(tid, u, mt, lab)

# B. onions: direct + tor2web proxies
proxies = ["", ".to", ".link", ".city", ".cab", ".direct", ".lt", ".sh", ".ws"]
for o in onions:
    for p in proxies:
        host = f"{o}.onion{p}"
        add(f"onion_{o}{p.replace('.','_')}", host, "domain", f"onion {o} proxy '{p or 'direct'}'")

# C. imgur files (PRIORITY 2 byte-diff hunt)
imgur_ids = ["8D7hN","DFQGJAN","KXLOP","hkdgl","m9sYK","vjuNp","zN4h51m","4gq25"]
for i in imgur_ids:
    add(f"imgur_{i}", f"imgur.com/{i}", "exact", f"imgur page {i}")
    add(f"iimgur_{i}", f"i.imgur.com/{i}*", "prefix_star", f"i.imgur file {i}")

# D. twitter
add("tw_420087183957966849","twitter.com/1231507051321/status/420087183957966849","exact","tweet 2014")
add("tw_684596461628223488","twitter.com/1231507051321/status/684596461628223488","exact","tweet 2016")
add("tw_3301actual","twitter.com/3301actual","prefix","3301actual account")
add("x_3301actual_759942242563821568","x.com/3301actual/status/759942242563821568","exact","3301actual tweet")

# E. onion aggregator / mirror hosts
for h in ["onion.link","onion.to","onion.city","tor2web.org","hiddenwiki.org","thehiddenwiki.org"]:
    add(f"host_{h.replace('.','_')}", f"{h}", "domain", f"proxy host {h} (may be huge)")

with open("targets.tsv","w",encoding="utf-8") as f:
    for tid,u,mt,lab in rows:
        f.write(f"{tid}\t{u}\t{mt}\t{lab}\n")
print(len(rows),"targets")
