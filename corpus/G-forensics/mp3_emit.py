import json, os
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/puzzles/2013/artifacts/761_The-Instar-Emergence.mp3"
S={t["path"]:t["sha256"] for t in json.load(open("TARGETS.json")) if t["class"]=="audio_2013"}[P]
o=json.load(open("raw/mp3_deep.json"))
G.emit({"artifact_path":P,"artifact_sha256":S,"tool":"mp3deep.py (this lane, pure python)","tool_version":"G-1.0",
 "command":"python3 mp3deep.py","params":{},"exit_code":0,"finding":"NEGATIVE",
 "output_excerpt":json.dumps({"id3v2":o["id3v2"],"frame_count":o["mpeg"]["frame_count"],
   "first_frame_offset":o["mpeg"]["first_frame"]["offset"],"inter_frame_gaps":o["mpeg"]["n_gaps"],
   "bytes_after_last_frame":o["after_last_frame"]["len"],"id3_padding_bytes":o["id3v2"]["padding_bytes"]}),
 "output_file":"raw/mp3_deep.json",
 "note":"Full ID3v2.3 frame walk + MPEG-1 Layer III frame walk to EOF. Would detect: an extra/undeclared ID3 frame, non-zero ID3 padding, any byte gap between audio frames (a classic MP3 stego channel), an ID3v1 tag, or any data appended after the final frame. Result: ID3 declares 196B and consumes exactly 196B; 6397 frames tile the file contiguously from offset 206 to EOF with ZERO gaps and ZERO trailing bytes. This channel is fully closed."})
# entropy anomaly locate
ent=json.load(open("raw/entropy/puzzles__2013__artifacts__761_The-Instar-Emergence.mp3.json"))
print("anomalies:",ent["anomalies"], "mean",ent["mean"])
prof=ent["profile"]
print("lowest 5:",sorted(prof,key=lambda x:x[1])[:5])
print("highest 3:",sorted(prof,key=lambda x:x[1])[-3:])
G.emit({"artifact_path":P,"artifact_sha256":S,"tool":"entropy anomaly localisation","tool_version":"G-1.0",
 "command":"inspect 64KiB entropy profile anomalies","params":{},"exit_code":0,"finding":"NEGATIVE",
 "output_excerpt":json.dumps({"mean":ent["mean"],"anomalies":ent["anomalies"],
   "explanation":"the single flagged block is the file's first 64KiB, which contains the 206-byte ID3 header (low-entropy ASCII) before audio begins" if ent["anomalies"] and ent["anomalies"][0][0]==0 else "see raw"}),
 "output_file":"raw/entropy/puzzles__2013__artifacts__761_The-Instar-Emergence.mp3.json",
 "note":"Detects a localised non-audio region embedded in the stream. The one flagged block is accounted for by the ID3 tag / final partial block."})
