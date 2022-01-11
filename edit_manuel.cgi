#!/usr/bin/perl

require './cassandra-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'manual_title'},"");

my @files = ( $config{'cassandra_conf'}, $config{'cassandra_logback'} , $config{'cassandra_topology_properties'} );

$in{"file"} ||= $files[0];
&indexof($in{'file'}, @files) >= 0 || &error($text{'manual_efile'});
print &ui_form_start("edit_manuel.cgi");
print &ui_select("file", $in{'file'},
			[ map { [ $_ ] } @files ]),"\n";
print &ui_submit($text{'manual_ok'});
print &ui_form_end();



print &text('manual_desc',"$in{'file'}");

print &ui_form_start("save_manual.cgi", "form-data");
print &ui_hidden("file", $in{'file'}),"\n";
my $data = &read_file_contents($in{'file'});
print &ui_textarea("data", $data, 20,80),"\n";
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("", $text{'index_return'});
