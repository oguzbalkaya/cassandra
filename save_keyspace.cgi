#! /usr/bin/perl

require './cassandra-lib.pl';

&ReadParse();
&error_setup($text{'keyspace_err'});
&error($text{'keyspace_nameerr'}) if(not ($in{'keyspace'}));


if($in{'strategy'} eq "SimpleStrategy")
{
	&create_simples_keyspace($in{'keyspace'},$in{'replication_factor'},$in{'durablewrites'});
}elsif($in{'strategy'} eq "NetworkTopologyStrategy"){
	&create_networktopologys_keyspace($in{'keyspace'},$in{'replication_factor'},$in{'datacenters'},$in{'durablewrites'});
}



&webmin_log("Create keyspace", undef, $in{'keyspace'});

&redirect("keyspaces.cgi");


