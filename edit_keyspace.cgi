#! /usr/bin/perl

require 'cassandra-lib.pl';
&ReadParse();
&error_setup($text{'error_editkeyspace'});
&ui_print_header(undef, $module_info{'desc'},"");
my @strategies=( "SimpleStrategy", "NetworkTopologyStrategy" );
&error($text{'keyspace_edit_keyspaceempty'}) if(not $in{'keyspace'});

my %keyspace_info=&get_keyspace_info($in{'keyspace'});
&error($text{'keyspace_edit_keyspacenotexist'}) if(not &is_keyspace_exists($in{'keyspace'}));

$in{'strategy'} ||= $keyspace_info{'strategy'};


print &ui_form_start('alter_keyspace.cgi');
print &ui_table_start($text{'keyspace_edit_title'}, "width=100%", 1);
 

print &ui_table_row($text{'keyspace_new_name'},$in{'keyspace'},30);

print &ui_table_row($text{'keyspace_new_strategy'},
	&ui_select_strategy_list($in{'strategy'},"edit_keyspace.cgi","&keyspace=$in{'keyspace'}",@strategies));




if($in{'strategy'} eq "NetworkTopologyStrategy"){

	print &ui_table_row($text{'keyspace_new_datacenters'},
		&ui_textbox("datacenters",$keyspace_info{'datacenters'},30));
	
	print &ui_table_row($text{'keyspace_new_replication'},
                &ui_textbox("replication_factor",$keyspace_info{'replication_factors'},30));
}else{
	print &ui_table_row($text{'keyspace_new_replication'},
        &ui_textbox("replication_factor","$keyspace_info{'replication_factor'}",30));
}


print &ui_table_row($text{'keyspace_new_durablewrites'},
        &ui_select("durablewrites", $keyspace_info{'durable_writes'}, [ "True","False" ]));


print &ui_table_row(&ui_submit($text{'keyspace_edit_editbutton'}));

print &ui_hidden("strategy", $in{'strategy'});
print &ui_hidden("old_strategy", $keyspace_info{'strategy'});
print &ui_hidden("keyspace", $keyspace_info{'name'});

print &ui_form_end();
print &ui_table_end();



print &ui_hr();

&table_list($in{'keyspace'});

print &ui_hr();


print &ui_table_start($text{'table_createtable'},"width=100%",2);
print "<table width=100%><tr>\n";
print "<td style='text-align:center'><form action=create_table.cgi\n>";
print "<input type=hidden name=xnavigation value=1>";
print "<input type=hidden name=keyspace_name value=$in{'keyspace'}>";
print "<input type=text name=table_name placeholder='$text{'createtable_placeholdertablename'}'>    ";
print "<input type=text name=fields placeholder='$text{'createtable_placeholderfields'}'>\n";
print "<input type=submit class='btn btn-success' value='$text{'table_createbutton'}'>\n";
print "</td></tr></form></table>";
print &ui_table_end();

print &ui_hr();


print &ui_table_start($text{'createudt_title'},"width=100%",2);
print "<table width=100%><tr>\n";
print "<td style='text-align:center'><form action=create_udt.cgi\n>";
print "<input type=hidden name=xnavigation value=1>";
print "<input type=hidden name=keyspace_name value=$in{'keyspace'}>";
print "<input type=text name=name placeholder='$text{'createudt_name_placeholder'}'>    ";
print "<input type=text name=count placeholder='$text{'createudt_countoftypes_placeholder'}'>\n";
print "<input type=submit class='btn btn-success' value='$text{'createudt_create_button'}'>\n";
print "</td></tr></form></table>";
print &ui_table_end();

print &ui_hr();

my @udtypes=&get_udtypes($in{'keyspace'});
my $length=@udtypes;
print &ui_table_start("User-defined types","width=100%",3);
if($length == 0){
	print "$text{'udtlist_noudt'}";

}else{
	print &ui_columns_start([
                $text{'udtlist_name'},
                $text{'udtlist_subtypes'},
                $text{'udtlist_delete'}
        ], "100%");
	foreach my $udtype(@udtypes){
		my $subs="";
		my $length=@{$udtype->{'subtypes'}};
		for(my $i=0;$i<$length;$i++){
			$subs=$subs. "($udtype->{'subtypes'}[$i], $udtype->{'subdatatypes'}[$i]),";
		}
		chop($subs);

		print &ui_columns_row(
				[ "<center>$udtype->{'name'}</center>","<center>$subs</center>","<a href='ask.cgi?type=dropudt&udt=".&urlize($udtype->{'name'})."&keyspace=".&urlize($in{'keyspace'})."'><center>".&ui_submit($text{'udtlist_delete'}) ."</center> </a>" ]);
        }
}
print &ui_columns_end();
print &ui_table_end();


&ui_print_footer("keyspaces.cgi", $text{'keyspacelist_return'},
                 "", $text{'index_return'});

