#!/usr/bin/perl
# ROUND 19 / G2 -- the reductions, written as a 2012 Perl author would write
# them, and run by the REAL perl.  gen_perl.py must match these element for
# element before it may produce a keystream.
#
#   ref_reduce.pl REDUCTION SEED N   ->  N comma-separated symbols
#
# For r26_lat this emits the LETTER index 0..25; the Latin->futhorc mapping is a
# repo-side step (skipdecode.eng_to_idx), not a Perl step, and validate.py
# applies it.
no warnings;
my ($red, $seed, $n) = @ARGV;
srand($seed + 0);
my @k;

if ($red eq 'r29') {
    push @k, int(rand(29)) for 1 .. $n;
}
elsif ($red eq 'r29_nodup') {
    my $last = -1;
    while (@k < $n) {
        my $x = int(rand(29));
        next if $x == $last;
        push @k, $x;
        $last = $x;
    }
}
elsif ($red eq 'r32_rej') {
    while (@k < $n) {
        my $x = int(rand(32));
        next if $x > 28;
        push @k, $x;
    }
}
elsif ($red eq 'r256_mod')  { push @k, int(rand(256))   % 29 for 1 .. $n; }
elsif ($red eq 'r2p32_mod') { push @k, int(rand(2**32)) % 29 for 1 .. $n; }
elsif ($red eq 'r255_mod')  { push @k, int(rand(255))   % 29 for 1 .. $n; }
elsif ($red eq 'r100_mod')  { push @k, int(rand(100))   % 29 for 1 .. $n; }
elsif ($red eq 'r1000_mod') { push @k, int(rand(1000))  % 29 for 1 .. $n; }
elsif ($red eq 'r26_lat')   { push @k, int(rand(26)) for 1 .. $n; }
else { die "unknown reduction $red\n"; }

print join(",", @k), "\n";
