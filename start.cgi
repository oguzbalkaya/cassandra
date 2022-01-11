#! /usr/bin/perl
#start.cgi
#Start the apache cassandra daemon

require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_start'});
my $err=&start_cassandra();
&error($err) if($err);
sleep(1);
&webmin_log("start");
&redirect("");
