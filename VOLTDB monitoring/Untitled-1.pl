#!/usr/bin/perl -w
use strict;

my $str  = 'abcadefaghi';
my $pat  = '(a.)';
my $repl = sub {"$1 "};

$str =~ s/$pat/&$repl/eg;
my @a=(1,2,31,4,5,6);
my @b=(11,21,31,41,51,61);
print "Index: $_ => \@a: $a[$_], \@b: $b[$_]\n" 
    for grep { $a[$_] != $b[$_] } 0 .. $#b;

my $ab="A dog once barked outside";
my @li= split /\s+/, $ab;

foreach(@li)
{
    foreach(@a)
    {
        print"$_";
    }
    # print"@a\t";

   
}
#   print"@a\t";