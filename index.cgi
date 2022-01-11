#!/usr/bin/perl

require 'cassandra-lib.pl';

my $ver = &get_cassandra_version() ? &text('index_version',&get_cassandra_version()):$text{'start_for_version'}; 
&ui_print_header(undef, $module_info{'desc'}, "", undef, 1, 1, undef,
        &help_search_link("cassandra", "man", "doc", "google"), undef, undef,
        $ver);


my $pid=&get_cassandra_pid();
if(not -e $config{'cassandra_conf'}){
	print $text{'conffile_err'};
}elsif(not -e $config{'cassandra_logback'}){
	print $text{'logback_err'};
}elsif(not -e $config{'cassandra_topology_properties'}){
	print $text{'topology_properties_err'};
}
elsif(&get_cassandra_version())
{
	#Keyspaces
	push(@links, "keyspaces.cgi");
	push(@titles, $text{'index_keyspaces'});
	push(@icons, "images/keyspaces.png");
	#Configurations list
	push(@links, "list_conf.cgi");
	push(@titles, $text{'index_listconf'});
	push(@icons, "images/edit_conf.png");
	#Edit manuel 
	push(@links, "edit_manuel.cgi");
	push(@titles, $text{'index_editmanuel'});
	push(@icons, "images/edit_manuel.png");
	#Run cql command
	push(@links, "run_cql_command.cgi");
	push(@titles, $text{'index_runcommand'});
	push(@icons, "images/run_command.gif");
	&icons_table(\@links, \@titles, \@icons, 4);


	print &ui_hr();
	
	print &ui_buttons_start();
	if($pid)
	{
	print &ui_buttons_row("stop.cgi", $text{'index_stop'}, $text{'index_stopmsg'});
	print &ui_buttons_row("reload.cgi", $text{'index_reload'}, $text{'index_reloadmsg'});
	}
	else
	{
	print &ui_buttons_row("start.cgi", $text{'index_start'}, $text{'index_startmsg'});

	}
	print &ui_buttons_end();	



}else{
	if($pid){
		my $err = `$config{'cql_command'} 2>&1`;
		print(&text('index_cassandraerr',$err));
		print &ui_buttons_row("stop.cgi", $text{'index_stop'}, $text{'index_stopmsg'});
        	print &ui_buttons_row("reload.cgi", $text{'index_reload'}, $text{'index_reloadmsg'});
	}
	else
	{
		print($text{'index_installerr'});
		print &ui_buttons_row("start.cgi", $text{'index_start'}, $text{'index_startmsg'});
	}
}
&ui_print_footer('/', $text{'index'});
