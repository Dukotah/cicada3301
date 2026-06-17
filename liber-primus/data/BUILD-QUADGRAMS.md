# Rebuilding the quadgram model

`english_quadgrams.txt` (committed) is derived from public-domain text. The raw
corpus is gitignored to keep the repo small. To rebuild:

```bash
cd liber-primus/data
# KJV (archaic register — matches LP), Moby Dick, Pride & Prejudice, War & Peace
for f in "10/10-0.txt:kjv.txt" "2701/2701-0.txt:moby.txt" \
         "1342/1342-0.txt:pride.txt" "2600/2600-0.txt:war.txt"; do
  curl -sL -A "Mozilla/5.0" -o "${f##*:}" "https://www.gutenberg.org/files/${f%%:*}"
done
python - <<'PY'
import re, collections
cnt=collections.Counter()
for fn in ["kjv.txt","moby.txt","pride.txt","war.txt"]:
    t=re.sub(r'[^A-Z]','',open(fn,encoding='utf-8',errors='ignore').read().upper())
    for i in range(len(t)-3): cnt[t[i:i+4]]+=1
open('english_quadgrams.txt','w',encoding='ascii').write(
    ''.join(f"{q} {c}\n" for q,c in cnt.most_common()))
print("quadgrams:",len(cnt))
PY
```
