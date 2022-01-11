#! /usr/bin/perl
require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_createudt'});

my @datatypes = &get_datatypes();

my @columns = ();
my $query="CREATE TYPE $in{\"keyspace_name\"}.$in{\"name\"} (";
for(my $i=0;$i<$in{'count'};$i++)
{
	&error(&text("createtable_emptycolumnerr",$i+1)) if(not $in{"typename_$i"});
	&error($text{'createtable_nameunique_err'}) if(grep { $_ eq $in{"typename_$i"} } @columns);
	push(@columns,$in{"typename_$i"});	
	$query = $query . " $in{\"typename_$i\"} $in{\"datatype_$i\"},";

}

chop($query);
$query=$query . ");";
my $c = `$config{'cql_command'} -e "$query" 2>&1`;

&error($c) if($?);
&webmin_log("Create user-defined type", undef, "$in{'keyspace_name'} - $in{'name'}");
&redirect("edit_keyspace.cgi?keyspace=$in{'keyspace_name'}&xnavigation=1");
