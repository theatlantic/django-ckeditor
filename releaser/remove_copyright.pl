#!/usr/bin/env perl

use File::Basename;

my @args = @ARGV;

for my $file (@args) {
    open(my $fh, "<", $file) or die("Could not open file '$file': $!\n");
    my $contents;
    {
        local $/ = \0;
        $contents = <$fh>;
    }
    close($fh);
    $contents =~ s/\r\n/\n/g;
    $contents =~ s/^\xEF\xBB\xBF//g;
    if ($contents =~ s/\/\*\n
    Copyright\ \(c\)\ 2003\-20\d\d\,\ CKSource\ \-\ Frederico\ Knabben\.\ All\ rights\ reserved\.\n
    For\ licensing\,\ see\ LICENSE\.html\ or\ http\:\/\/ckeditor\.com\/license\n
    \*\/\n
    \n//xsg) {
        $contents =~ s/^\r?\n//sg;
        open(my $fh, ">", $file) or die("Could not open file '$file': $!\n");
        print $fh $contents;
        close($fh);
    }
}