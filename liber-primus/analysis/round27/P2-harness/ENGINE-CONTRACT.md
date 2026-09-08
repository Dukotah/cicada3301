# Round 27 / P2 — CLI contract the P1 C engine (`grind27`) must satisfy

The harness (`engine.py`) drives the binary through exactly three modes. P1 either
implements this interface or edits the one adapter file `P2-harness/engine.py` to match
what it built — the checks themselves never construct command lines.

Binary location probed (first hit wins):
`P1-engine/grind27`, `P1-engine/build/grind27`, `$GRIND27` env var.
LM export probed: `P1-engine/panel_lm.f32` (9×24389 LE float32 row-major from
`round19/I2/models/panel.npz["LM"]`; expected sha256
`14a23d3619fa02dfb6aa20efafdd0fc0ff633c83d8dc5f02ac4d5d035b996297`).

Common flags (every invocation): `--vectors <P0-spec/vectors.json> --lm <panel_lm.f32>`
(engine loads C_SCREEN, panel mu/sd @ n120, quadgram path/floor, CAND_BAR from vectors.json).

## mode score — per-seed scoring (used by check_vectors, check_false_reject, check_r25_repro)

```
grind27 --vectors V --lm LM --mode score --seeds <seeds.txt> --out <out.jsonl> [--full] [--cipher <c.json>]
```

- `seeds.txt`: one decimal u32 per line.
- Output: one JSON object per line, **in input order**:
  minimal `{"seed": <u32>, "pmax": <double>}`; with `--full` additionally
  `"ks128": [128 ints], "plain_idx": [120 ints], "ptr_end": int, "n_skips": int, "nchars": int`.
- `pmax` printed with `%.17g`.
- `--cipher`: JSON `{"cipher_idx": [...]}` — overrides C_SCREEN with the first 120 entries.

## mode sweep — banded live sweep (used by check_drill, bench)

```
grind27 --vectors V --lm LM --mode sweep --band-start <u64> --band-end <u64> --threads <n> \
        --out <candidates.jsonl> [--cipher <c.json>] [--progress-dir <dir>]
```

- Screens every w in [band-start, band-end); appends `{"seed": w, "pmax": <double>}` to
  `--out` for every `pmax >= 5.0` (CAND_BAR from vectors.json; never compares to 7.3835).
- On exit prints one JSON summary line to stdout containing at least
  `{"mode":"sweep","seeds_done":N,"elapsed_s":S}` (extra keys fine).
- `--progress-dir`: optional `progress_w{i}.json` checkpoints per SPEC §6.

## mode self-test — the frozen planted screen (used by check_drill)

```
grind27 --vectors V --lm LM --mode self-test
```

- Decodes `vectors.json["planted_stage_a"]["cipher_idx_120"]` with seed 777's keystream
  through the identical stage-A config.
- Prints one JSON line: `{"mode":"self-test","seed":777,"pmax":<double>,"candidate":true|false}`.
- Exit 0 iff candidate (pmax >= 5.0). Expected pmax `17.93115850976196` ± 1e-9.

## Harness exit-code convention (all checks)

`0` PASS · `1` FAIL · `2` BLOCKED-ON-BINARY (binary/LM not found — Python-side portions
still ran and their results are printed).
