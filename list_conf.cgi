#! /usr/bin/perl

require './cassandra-lib.pl';
&ReadParse();
&ui_print_header(undef, $module_info{'desc'},"");
my @cassandra_config = &get_cassandra_config();


print &ui_form_start("save_config.cgi");
print &ui_table_start($text{'listconf_allconf'}, "width=90%", 4);
for my $conf(@cassandra_config)
{
	$conf->{'name'}=~s/ //g;
        print &ui_table_row($conf->{'name'},
        &ui_textbox($conf->{'name'}, $conf->{'value'}, 30));
        print &ui_hidden("$conf->{'name'}_line","$conf->{'line'}");

} 

print &ui_table_end();
print &ui_submit($text{'listconf_save'});
print &ui_form_end();

&ui_print_footer("", $text{'index_return'});
