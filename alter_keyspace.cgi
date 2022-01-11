#! /usr/bin/perl

require './cassandra-lib.pl';

&ReadParse();
&error_setup($text{'keyspace_err'});

if($in{'strategy'} eq "SimpleStrategy")
{
	&alter_simples_keyspace($in{'keyspace'},$in{'replication_factor'},$in{'durablewrites'},$in{'strategy'},$in{'old_strategy'});
}elsif($in{'strategy'} eq "NetworkTopologyStrategy"){
	&alter_networktopologys_keyspace($in{'keyspace'},$in{'replication_factor'},$in{'datacenters'},$in{'durablewrites'},$in{'strategy'},$in{'old_strategy'});
}



&webmin_log("Alter keyspace", undef, $in{'keyspace'});


&redirect("edit_keyspace.cgi?keyspace=$in{'keyspace'}");


