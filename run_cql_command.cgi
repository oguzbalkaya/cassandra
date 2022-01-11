#!/usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&ui_print_header(undef, $module_info{'desc'},"");
&error_setup($text{'error_runcommand'});
if($in{'command'}){
	my $c=`$config{'cql_command'} -e "$in{'command'}" 2>&1`;
	print &ui_table_start($text{'runcqlcommand_output'},"width=100%",3);
	
	print ">> $in{'command'}<br><br>";
	
	print $c;
	print &ui_table_end();
}



print &ui_table_start($text{'runcqlcommand_header'},"width=100%",2);
print "<table width=100%><tr>\n";
print "<td style='text-align:center'><form action=run_cql_command.cgi\n>";
print "<input type=hidden name=xnavigation value=1>";
print "<textarea name=command style='width:50%' placeholder='$text{'runcqlcommand_commandplaceholder'}'></textarea>";
print "<br><input type=submit class='btn btn-success' value='$text{'runcqlcommand_runbutton'}' : '>\n";
print "</td></tr></form></table>";
print &ui_table_end();


&webmin_log("run cql command : $in{'command'}");
ui_print_footer("", $text{'index_return'});
