#!/usr/bin/env perl

use strict;
use warnings;

use POSIX qw(strftime);

my $base36_symbols = join '', '0'..'9', 'A'..'Z';

sub base36 {
    my ($val) = @_;
    $val = int($val);
    my $b36 = '';
    my $sign = ($val > 0) ? '' : '-';
    $val = abs($val);
    while ($val) {
        $b36 = substr($base36_symbols, $val % 36, 1) . $b36;
        $val = int $val / 36;
    }
    return ($b36) ? $sign . $b36 : '0';
}

my @ymdh = split /\s/, strftime("%y %m %d %H", gmtime);

$ymdh[1] = $ymdh[1] - 1;

print join("", map { base36($_) } @ymdh), "\n";
