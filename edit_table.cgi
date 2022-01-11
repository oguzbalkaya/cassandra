#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_edittable'});
&ui_print_header(undef, $module_info{'desc'},"");
my @table_options=&get_table_options($in{'keyspace'},$in{'table'});


print &ui_hidden_start("Columns","columns",1);

&list_table_columns($in{'keyspace'},$in{'table'});
print &ui_table_start($text{'tableedit_addcolumns'},"width=100%",2);
print "<table width=100%><tr>\n";
print "<td style='text-align:center'><form action=add_columns.cgi\n>";
print "<input type=hidden name=xnavigation value=1>";
print "<input type=hidden name=keyspace_name value=$in{'keyspace'}>";
print "<input type=hidden name=table_name value=$in{'table'}>";
print "<input type=text name=fields placeholder='$text{'tableedit_columnsplaceholder'}'>\n";
print "<input type=submit class='btn btn-success' value='$text{'tableedit_addcolumns_button'}'>\n";
print "</td></tr></form></table>";
print &ui_table_end();

print &ui_hidden_end();

print &ui_hr();


print &ui_hidden_start($text{'tableedit_others'},"options",0);

print &ui_form_start('alter_table_options.cgi');
print &ui_columns_start([
                        $text{'tableedit_option'},
                        $text{'tableedit_value'}
        ]);

foreach my $option(@table_options){
	print &ui_columns_row(
		[ $option->{'option'}, &ui_textbox($option->{'option'},$option->{'value'}) ]
	);
}
print &ui_columns_end();
print &ui_hidden("keyspace",$in{'keyspace'});
print &ui_hidden("table", $in{'table'});
print &ui_submit($text{'tableedit_save'});
print &ui_reset($text{'tableedit_reset'});
print &ui_form_end();
print &ui_hidden_end();




&ui_print_footer("edit_keyspace.cgi?keyspace=$in{'keyspace'}", &text("keyspaceinfo_return",$in{'keyspace'}),"",$text{'index_return'});

