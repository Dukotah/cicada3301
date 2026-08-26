#!/usr/bin/perl
# ROUND 19 / G2 -- reference-vector emitter.
#
# Emits, from the REAL perl binary on this box, the exact quantities the Python
# reimplementation in gen_perl.py must reproduce byte-for-byte.
#
#   mode "raw"   SEED N       -> N lines of "%.17g", the raw Drand01() == drand48() value
#   mode "r29"   SEED N       -> one line, N comma-separated int(rand(29)) draws
#   mode "rN"    SEED N M     -> one line, N comma-separated int(rand(M)) draws
#   mode "coerce" ARG         -> one line "ret\tfirst8" for srand(ARG)
#
# Perl 5.14.2 semantics being targeted (verified against the 5.14.2 tarball,
# md5 3306fbaf976dcebdcd49b2ac0be00eb9):
#   config_h.SH:2131  #define Drand01()      drand48()
#   config_h.SH:2133  #define seedDrand01(x) srand48((Rand_seed_t)x)
#   Configure:19280   drand48 is the FIRST choice whenever the libc has it
#   pp.c pp_srand     const UV anum = (MAXARG < 1) ? seed() : POPu;
#   pp.c pp_rand      value = POPn (or 1.0); value *= Drand01();
no warnings;
my $mode = shift @ARGV;

if ($mode eq 'raw') {
    my ($seed, $n) = @ARGV;
    srand($seed + 0);
    printf("%.17g\n", rand()) for 1 .. $n;
}
elsif ($mode eq 'r29') {
    my ($seed, $n) = @ARGV;
    srand($seed + 0);
    my @k;
    push @k, int(rand(29)) for 1 .. $n;
    print join(",", @k), "\n";
}
elsif ($mode eq 'rN') {
    my ($seed, $n, $m) = @ARGV;
    srand($seed + 0);
    my @k;
    push @k, int(rand($m)) for 1 .. $n;
    print join(",", @k), "\n";
}
elsif ($mode eq 'coerce') {
    my $arg = $ARGV[0];
    my $ret = srand($arg);
    my @k;
    push @k, int(rand(29)) for 1 .. 8;
    print "$ret\t", join(",", @k), "\n";
}
else {
    die "usage: ref_perl.pl raw|r29|rN|coerce ...\n";
}
