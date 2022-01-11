#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_droptable'});
&redirect("") if(not $in{'keyspace'} || not $in{'table'});
&drop_table($in{'keyspace'},$in{'table'});

&webmin_log("Drop table", undef, "$in{'keyspace'}.$in{'table'}");

&redirect("edit_keyspace.cgi?keyspace=$in{'keyspace'}");
