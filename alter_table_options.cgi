#!/usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_altertableoptions'});
&error($text{'keyspace_edit_keyspacenotexist'}) if(not &is_keyspace_exists($in{'keyspace'}));
&error($text{'tabletruncate_notexisterr'}) if(not &is_table_exists($in{'keyspace'},$in{'table'}));


my $query = "ALTER TABLE $in{'keyspace'}.$in{'table'} WITH";
for(keys %in){
	next if($_ eq "CLUSTERING ORDER BY" || $_ eq "keyspace" || $_ eq "table");
	$query = $query . " $_ = $in{$_} AND";
}


$query=substr($query,0,-3);

my $c = `$config{'cql_command'} -e "$query" 2>&1`;
&error($c) if($?);

&webmin_log("Alter table options", undef, "$in{'table'}.$in{'keyspace'}");
&redirect("edit_table.cgi?keyspace=$in{'keyspace'}&table=$in{'table'}&xnavigation=1");
