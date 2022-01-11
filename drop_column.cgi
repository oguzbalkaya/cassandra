#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_dropcolumn'});

&error($text{'columndrop_keyspaceemptyerr'}) if(not $in{'keyspace'});
&error($text{'columndrop_tableemptyerr'}) if(not $in{'table'});
&error($text{'columndrop_columnemptyerr'}) if(not $in{'column'});


&drop_column($in{'keyspace'},$in{'table'},$in{'column'});

&webmin_log("Drop column", undef, "$in{'table'}.$in{'keyspace'} - $in{'column'}");
&redirect("edit_table.cgi?table=".&urlize($in{'table'})."&keyspace=".&urlize($in{'keyspace'})."");
