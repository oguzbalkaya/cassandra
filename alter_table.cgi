#! /usr/bin/perl
require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_altertable'});
my @datatypes = &get_datatypes($in{'keyspace'});


my @columns = ();
my $query="ALTER TABLE $in{'keyspace'}.$in{'table'} ADD (";

for(my $i=0;$i<$in{'fields'};$i++)
{
	&error(&text("createtable_emptycolumnerr",$i+1)) if(not $in{"column_$i"});
	&error($text{'column_exist_error'}) if(grep { $_ eq $in{"column_$i"} } @columns);
	push(@columns,$in{"column_$i"});
	
	my $isstatic = $in{"static_$i"} eq 'yes' ? "static":"";	
	
	$query = $query . " $in{\"column_$i\"} $in{\"datatype_$i\"} $isstatic ,";

}

chop($query);

$query = $query . " )";



my $c = `$config{'cql_command'} -e "$query" 2>&1`;



&error("$c") if($?);
&webmin_log("Alter table", undef, "$in{'keyspace'}.$in{'table'}");
&redirect("edit_table.cgi?keyspace=".&urlize($in{'keyspace'})."&table=".&urlize($in{'table'})."&xnavigation=1");

