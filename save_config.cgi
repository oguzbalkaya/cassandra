#! /usr/bin/perl
require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_saveconfig'});

my @problem_fields=("-/var/lib/cassandra/data","-class_name","parameters","keystore","keystore_password","require_client_auth","enabled","-keystore");


my $lref=&read_file_lines($config{'cassandra_conf'});
foreach my $conf(keys %in){
	next if($conf =~ /_line$/);
	chop($conf) if($conf =~ /\n$/);
	next if(grep { $_ eq $conf } @problem_fields);
	my $newvalue = $in{"$conf"};
	$lref->[$in{"$conf"."_line"}] = "$conf: $in{\"$conf\"}";
}


&flush_file_lines($config{'cassandra_conf'});
&webmin_log("Save config", undef,"");
&redirect("list_conf.cgi");
