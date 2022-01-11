#! /usr/bin/perl
#start.cgi
#Start the apache cassandra daemon

require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_stop'});
my $err=&stop_cassandra();
&error($err) if($err);
&webmin_log("stop");
&redirect("");
