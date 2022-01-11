#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_dropkeyspace'});
&redirect("") if(not $in{'keyspace'});

&drop_keyspace($in{'keyspace'});
&webmin_log("Drop keyspace", undef, $in{'keyspace'});
&redirect("keyspaces.cgi");
