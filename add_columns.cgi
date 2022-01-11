#! /usr/bin/perl

require './cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_addcolumn'});
&ui_print_header(undef, $module_info{'desc'},"");
&error($text{'createtable_fielderr'}) if($in{'fields'} < 1);
&error($text{'keyspace_nameexisterr'}) if(not (&is_keyspace_exists($in{'keyspace_name'})));
&error($text{'createtable_tablenameempty'}) if(not $in{'table_name'});
&error($text{'createtable_tableexisterr'}) if(not &is_table_exists($in{'keyspace_name'},$in{'table_name'}));

&add_columns_list($in{'fields'},$in{'keyspace_name'},$in{'table_name'});

&ui_print_footer("edit_keyspace.cgi?keyspace=$in{'keyspace_name'}", &text('keyspaceinfo_return',$in{'keyspace_name'}));
