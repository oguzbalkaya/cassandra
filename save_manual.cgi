#! /usr/bin/perl

require './cassandra-lib.pl';
&error_setup($text{'manual_err'});
&ReadParseMime();


my @files = ( $config{'cassandra_conf'}, $config{'cassandra_logback'} , $config{'cassandra_topology_properties'} );
$in{'file'} ||= $files[0];
&indexof($in{'file'}, @files) >= 0 || &error($text{'manual_efile'});



&open_lock_tempfile(DATA,">$in{'file'}");
&print_tempfile(DATA, $in{'data'});
&close_tempfile(DATA);

&webmin_log("Edit manual", undef, $in{'file'});
&redirect("");
