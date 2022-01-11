#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_truncatetable'});
&rediretct("") if(not $in{'keyspace'} || not $in{'table'});

&truncate_table($in{'keyspace'},$in{'table'});
&webmin_log("Truncate table", undef, "$in{'keyspace'}.$in{'table'}");
&redirect("edit_keyspace.cgi?keyspace=$in{'keyspace'}");
