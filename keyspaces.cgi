#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'keyspace_err'});
&ui_print_header(undef, $module_info{'desc'},"");

my @strategies=( "SimpleStrategy", "NetworkTopologyStrategy" );
$in{'strategy'} ||= $strategies[0];
&indexof($in{'strategy'}, @strategies) >= 0 || &error($text{'strategy_err'});



print &ui_form_start('save_keyspace.cgi');
print &ui_table_start($text{'keyspace_new_title'}, "width=100%", 1);

print &ui_table_row($text{'keyspace_new_strategy'},
	&ui_select_strategy_list($in{'strategy'},"keyspaces.cgi","",@strategies));

print &ui_table_row($text{'keyspace_new_name'},
	&ui_textbox("keyspace","",30));



if($in{'strategy'} eq "NetworkTopologyStrategy"){

	print &ui_table_row($text{'keyspace_new_datacenters'},
		&ui_textbox("datacenters","",30));
	
	print &ui_table_row($text{'keyspace_new_replication'},
                &ui_textbox("replication_factor","",30));
}else{
	print &ui_table_row($text{'keyspace_new_replication_simple'},
        &ui_textbox("replication_factor","",30));
}


print &ui_table_row($text{'keyspace_new_durablewrites'},
        &ui_select("durablewrites", "True", [ "True","False" ]));



print &ui_hidden("strategy", $in{'strategy'});

print &ui_table_row(&ui_reset($text{'button_reset'}),&ui_submit($text{'keyspace_new_createbutton'}));

print &ui_table_end();

print &ui_form_end();

print &ui_hr();

print &ui_table_start($text{'keyspace_list'}, "width=90%", 3);

&list_keyspaces();

print &ui_table_end();

&ui_print_footer("", $text{'index_return'});
