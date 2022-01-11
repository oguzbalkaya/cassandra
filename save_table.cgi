#! /usr/bin/perl
require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_createtable'});

my @datatypes = &get_datatypes($in{'keyspace_name'});

my @others = ("comment","speculative_retry","cdc","additional_write_policy","gc_grace_seconds","bloom_filter_fp_chance","default_time_to_live","compaction","compression","caching","memtable_flush_period_in_ms","read_repair");


my @columns = ();
my $query="CREATE TABLE $in{\"keyspace_name\"}.$in{\"table_name\"} (";
my $isstatic="";
for(my $i=0;$i<$in{'fields'};$i++)
{
	&error(&text("createtable_emptycolumnerr",$i+1)) if(not $in{"column_$i"});
	&error($text{'createtable_primarykeyemptyerr'}) if(not $in{'primarykey'});
	&error($text{'createtable_nameunique_err'}) if(grep { $_ eq $in{"column_$i"} } @columns);
	$isstatic="static" if($in{"static_$i"} eq 'yes');
	push(@columns,$in{"column_$i"});	
	$query = $query . " $in{\"column_$i\"} $in{\"datatype_$i\"} $isstatic,";

}

$query = $query . " PRIMARY KEY ($in{'primarykey'}))";
my $clustering="";
if ($in{'CLUSTERING ORDER BY'}){
	$clustering = "CLUSTERING ORDER BY ($in{'CLUSTERING ORDER BY'}) AND";
}


my $othersq="";
foreach my $opt(@others){
	if($in{"$opt"}){
		$othersq = $othersq . " $opt = '$in{\"$opt\"}' AND";
	}
}


if($othersq ne ""){
	$othersq = substr($othersq, 0, -3);
	$query = $query . " WITH $clustering " . $othersq;
}


my $c = `$config{'cql_command'} -e "$query" 2>&1`;

&error($c) if($?);
&webmin_log("Create table", undef, "$in{'keyspace_name'}.$in{'table_name'}");
&redirect("edit_keyspace.cgi?keyspace=$in{'keyspace_name'}&xnavigation=1");
