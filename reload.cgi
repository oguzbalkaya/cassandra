#! /usr/bin/perl
#reload.cgi
#Retart the apache cassandra daemon

require './cassandra-lib.pl';
&ReadParse();
my $reload = `$config{'restart_command'} 2>&1 </dev/null`;
&webmin_log("restart");
sleep(2);
&redirect("");
