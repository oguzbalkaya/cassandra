#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_dropudt'});
&error($text{'columndrop_keyspaceemptyerr'}) if(not $in{'keyspace'});
&error($text{'udtdrop_emptyerr'}) if(not $in{'udt'});

&drop_udt($in{'keyspace'},$in{'udt'});

&webmin_log("Drop udt", undef, "$in{'keyspace'} - $in{'udt'}");
&redirect("edit_keyspace.cgi?&keyspace=".&urlize($in{'keyspace'})."");
