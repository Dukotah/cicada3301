<?php
/* Round 28 / L4 -- PHP mt_rand reference-vector emitter.
 *
 * This is the REAL /usr/bin/php (8.5.4) exercising both engine modes:
 *   MT_RAND_MT19937  -- canonical MT19937 twist (PHP >= 7.1 default)
 *   MT_RAND_PHP      -- the documented pre-7.1 broken twist, kept by PHP for
 *                       reproducibility of legacy sequences (deprecated 8.3+,
 *                       still bit-exact; deprecation notices suppressed below)
 *
 * For each requested seed it emits JSON with, per mode:
 *   raw     : mt_rand() with no args  = temper(next_u32()) >> 1   (31-bit)
 *   scaled  : RAND_RANGE_BADSCALING of the SAME raw stream to [0,28] --
 *             (int)(29.0 * (r / 2147483648.0)), the exact pre-7.1 mt_rand(0,28)
 *             arithmetic (double math done here IN PHP, so the reference owns it)
 *   mod29   : r % 29 of the same raw stream (the naive idiom)
 *   range legacy check (MT_RAND_PHP only): mt_rand(0,28) called directly MUST
 *             equal `scaled`, proving PHP still routes MT_RAND_PHP ranges through
 *             RAND_RANGE_BADSCALING (ext/random compatibility path).
 *
 * usage: php ref_php.php '<json list of seeds>' <ndraws>
 */
error_reporting(E_ALL & ~E_DEPRECATED);
$seeds = json_decode($argv[1]);
$n = (int)$argv[2];
$out = ["getrandmax" => mt_getrandmax(), "php_version" => PHP_VERSION, "seeds" => []];
foreach ($seeds as $s) {
    $row = ["seed" => $s];
    foreach ([["mt", MT_RAND_MT19937], ["php", MT_RAND_PHP]] as [$name, $mode]) {
        mt_srand($s, $mode);
        $raw = []; $scaled = []; $mod = [];
        for ($i = 0; $i < $n; $i++) {
            $r = mt_rand();                                   /* temper >> 1 */
            $raw[] = $r;
            $scaled[] = 0 + (int)((double)(28 - 0 + 1.0) * ($r / (2147483647 + 1.0)));
            $mod[] = $r % 29;
        }
        $row[$name] = ["raw" => $raw, "scaled" => $scaled, "mod29" => $mod];
        if ($mode === MT_RAND_PHP) {
            /* legacy range path check: same seed, direct mt_rand(0,28) */
            mt_srand($s, MT_RAND_PHP);
            $rng = [];
            for ($i = 0; $i < $n; $i++) $rng[] = mt_rand(0, 28);
            $row["php_range_direct"] = $rng;
            $row["php_range_matches_badscaling"] = ($rng === $scaled);
        } else {
            /* modern mode range check: mt_rand(0,28) uses uniform rejection, NOT
             * badscaling -- recorded so the divergence is documented, not assumed */
            mt_srand($s, MT_RAND_MT19937);
            $rng = [];
            for ($i = 0; $i < $n; $i++) $rng[] = mt_rand(0, 28);
            $row["mt_range_direct_modern"] = array_slice($rng, 0, 16);
        }
    }
    $out["seeds"][] = $row;
}
echo json_encode($out), "\n";
