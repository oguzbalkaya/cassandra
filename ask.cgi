#! /usr/bin/perl

require './cassandra-lib.pl';
&ReadParse();

&redirect("") if(not $in{'type'});

if($in{'type'} eq "keyspacedelete")
{
	&ui_print_header(undef, $module_info{'desc'},"");	
	&redirect("") if(not $in{'keyspace'});
	print &text("keyspacedelete_ask",$in{'keyspace'});
	print &ui_hr();
	print "<a href='drop_keyspace.cgi?keyspace=".&urlize($in{'keyspace'})."'>".&ui_submit($text{'keyspace_list_delete'})."</a>";
	&ui_print_footer("keyspaces.cgi", $text{'keyspacelist_return'});
}
elsif($in{'type'} eq "tabledelete")
{
	&ui_print_header(undef, $module_info{'desc'},"");
	&redirect("") if(not $in{'keyspace'});
	&redirect("") if(not $in{'table'});
	print &text("tabledelete_ask",$in{'table'},$in{'keyspace'});
	print &ui_hr();
	print "<a href='drop_table.cgi?table=".&urlize($in{'table'})."&keyspace=".&urlize($in{'keyspace'})."'>".&ui_submit($text{'tablelist_delete'})."</a>";
	&ui_print_footer("edit_keyspace.cgi?keyspace=".&urlize($in{'keyspace'})."", $text{'tablelist_return'});
}
elsif($in{'type'} eq "tabletruncate")
{
	&ui_print_header(undef, $module_info{'desc'},"");
	&redirect("") if(not $in{'keyspace'});
        &redirect("") if(not $in{'table'});
	print &text("tabletruncate_ask",$in{'table'},$in{'keyspace'});
	print &ui_hr();
	print "<a href='truncate_table.cgi?table=".&urlize($in{'table'})."&keyspace=".&urlize($in{'keyspace'})."'>".&ui_submit($text{'tablelist_truncate'})."</a>";
	&ui_print_footer("edit_keyspace.cgi?keyspace=".&urlize($in{'keyspace'})."", $text{'tablelist_return'});
}
elsif($in{'type'} eq "columndrop"){
	&ui_print_header(undef, $module_info{'desc'},"");
	&redirect("") if(not $in{'keyspace'} || not $in{'table'} || not $in{'column'});
	print &text("tableedit_dropcolumn_ask",$in{'column'},$in{'table'},$in{'keyspace'});
	print &ui_hr();
	print "<a href='drop_column.cgi?column=".&urlize($in{'column'})."&table=".&urlize($in{'table'})."&keyspace=".&urlize($in{'keyspace'})."'>".&ui_submit($text{'tableedit_deletecolumn_button'})."</a>";
	&ui_print_footer("edit_table.cgi?table=".&urlize($in{'table'})."&keyspace=".&urlize($in{'keyspace'})."", &text('tableedit_return',$in{'table'}));
}
elsif($in{'type'} eq "dropudt"){
	&ui_print_header(undef, $module_info{'desc'},"");
	&redirect("") if(not $in{'keyspace'} || not $in{'udt'});
	print &text("udtdrop_ask",$in{'udt'},$in{'keyspace'});
        print &ui_hr();
	print "<a href='drop_udt.cgi?udt=".&urlize($in{'udt'})."&keyspace=".&urlize($in{'keyspace'})."'>".&ui_submit($text{'udtlist_delete'})."</a>";
        &ui_print_footer("edit_keyspace.cgi?&keyspace=".&urlize($in{'keyspace'})."", &text('keyspacelist_return',$in{'keyspace'}));


}
else
{
	&redirect("");
}
	
