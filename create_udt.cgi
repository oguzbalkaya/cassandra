#! /usr/bin/perl

require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_createudt'});
&ui_print_header(undef, $module_info{'desc'},"");
&error($text{'createudt_counterr'}) if($in{'count'} < 1);
&error($text{'keyspace_nameexisterr'}) if(not (&is_keyspace_exists($in{'keyspace_name'})));

&createudt_list($in{'keyspace_name'},$in{'count'},$in{'name'});


&ui_print_footer("edit_keyspace.cgi?keyspace=$in{'keyspace_name'}", &text('keyspaceinfo_return',$in{'keyspace_name'}));
