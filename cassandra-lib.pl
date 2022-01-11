#! /usr/bin/perl

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();

sub get_cassandra_pid
{
	if(-e $config{'pid_file'}){
		return `cat $config{'pid_file'}`;
	}
	else
	{
		return 0;
	}
}	


sub get_cassandra_config
{
	open(CONF,"<","$config{'cassandra_conf'}");
	my @cassandra_config=();
	my $line=-1;
	while(<CONF>){
		$_ =~ s/\r//g;
		$_ =~ s/^\s*#.*$//g;
		$line++;
		next if($_ eq "\n");
		my($name, $value)=split(":", $_,2);
		$name =~ s/ //g;
		$value =~ s/ //g;
		my $c = { 'name' => $name,
			  'value' => $value,
			  'line' => $line};
		push(@cassandra_config,$c);
	}
	return @cassandra_config;
}	

sub get_cassandra_version
{
	my $c=`$config{'cql_command'} -e "show version"; 2>&1`;
	my @data = split(/\|/,$c);
	my @data = split(/ /,$data[1]);
	my $version = $data[2];
	return $version;
}

sub restart_cassandra
{
	if($config{'restart_command'}){
		my $out=`$config{'restart_command'} 2>&1 </dev/null`;
		&kill_logged('HUP', $pid);
		return "<pre>$out</pre>" if($?);
	}
	else{
		my $pid=&get_cassandra_pid();
		$pid || return "err";
		&kill_logged('HUP', $pid);
	}
	return undef;
}



sub start_cassandra
{
	if($config{'start_command'}){
		my $out=`$config{'start_command'} 2>&1 </dev/null`;
		return "<pre>$out</pre>" if($?);
	}else
	{
		my $out=`systemctl start cassandra 2>&1 </dev/null`;
		return "<pre>$out</pre>" if($?);
	}
	return undef;
}

sub stop_cassandra
{
	if($config{'stop_command'}){
		my $out=`$config{'stop_command'} 2>&1 </dev/null`;
		return "<pre>$out</pre>" if($?);
	}else{
		my $pid=&get_cassandra_pid();
		$pid || return "err";
		&kill_logged('TERM',$pid);
	}
	return undef;
}

sub is_keyspace_exists
{
	my $keyspace_name = shift;
	my $count=`$config{'cql_command'} -e "DESCRIBE KEYSPACES;" | grep -woc "$keyspace_name"`;
	if($count != 0){
		return 1;
	}else{
		return 0;
	}
}


sub is_table_exists
{
	my($keyspace_name,$table_name)=@_;
	my $count=`$config{'cql_command'} -e "SELECT COUNT(table_name) FROM system_schema.tables WHERE keyspace_name='$keyspace_name' AND table_name='$table_name'" | tail -n +4 | head -n -2`;
	$count=~s/ //g;
	return $count == 1 ? 1:0;
}


sub ui_select_strategy_list
{
	my($strategy,$link,$extras,@strategies) = @_;
	my $options="";
	for my $s(@strategies){
		my $selected="";
		if($strategy eq $s){
			$selected = "selected";
		}
		$options = $options."<option value='$link?strategy=$s$extras&xnavigation=1' $selected>$s</option>";
	}
	return "
		<form method=get>
		<select onchange='location = this.value'>
		$options
		</select>
		</form>";
}



sub create_simples_keyspace
{					
	my($keyspace_name,$replication_factor,$durable_writes)=@_;
	&error($text{'keyspace_nameerr'}) if(not ($keyspace_name));
	&error($text{'keyspace_nameexisterr'}) if(&is_keyspace_exists($keyspace_name));
	&error($text{'keyspace_replicationerr'}) if($replication_factor == 0 || $replication_factor =~ /\D/);
	&error($text{'keyspace_durablewriteserr'}) if($durable_writes ne "True" && $durable_writes ne "False");

	my $c = `$config{'cql_command'} -e "CREATE KEYSPACE $keyspace_name with replication={'class':'SimpleStrategy','replication_factor':$replication_factor} AND DURABLE_WRITES = $durable_writes;" 2>&1`;
	
	
	&error($c) if ($?);		
}

sub create_networktopologys_keyspace{
	my($keyspace_name,$replication_factor,$datacenter,$durable_writes)=@_;
	&error($text{'keyspace_nameerr'}) if(not ($keyspace_name));
	&error($text{'keyspace_nameexisterr'}) if(&is_keyspace_exists($keyspace_name));
	&error($text{'keyspace_durablewriteserr'}) if($durable_writes ne "True" && $durable_writes ne "False");
	my @replication_factors=split(/,/,$replication_factor);
	my @datacenters = split(/,/,$datacenter);
	my $countofreplication=@replication_factors;
	my $countofdatacenters=@datacenters;
	my $replications = "";
	&error($text{'keyspace_repdataneerr'}) if($countofreplication != $countofdatacenters);
	for(my $i=0;$i<$countofreplication;$i++){
		&error($text{'keyspace_replicationerr'}) if($replication_factors[$i] == 0 || $replication_factors[$i] =~ /\D/);
		$replications = $replications." '$datacenters[$i]' : $replication_factors[$i],";
	}
	chop($replications);
	
	my $c = `$config{'cql_command'} -e "CREATE KEYSPACE $keyspace_name with replication={'class':'NetworkTopologyStrategy',$replications } and durable_writes = $durable_writes;" 2>&1`;
	&error($c) if ($?);
}

sub alter_networktopologys_keyspace{
	my($keyspace,$replication_factor,$datacenter,$durable_writes,$new_strategy,$old_strategy)=@_;
	&error($text{'keyspace_nameexisterr'}) if(not (&is_keyspace_exists($keyspace)));
	&error($text{'keyspace_durablewriteserr'}) if($durable_writes ne "True" && $durable_writes ne "False");
	my @replication_factors=split(/,/,$replication_factor);
	my @datacenters=split(/,/,$datacenter);
	my $countofreplication=@replication_factors;
	my $countofdatacenters=@datacenters;
	my $replications="";
	&error($text{'keyspace_repdatanerr'}) if($countofdatacenters != $countofreplication);
	for(my $i=0;$i<$countofreplication;$i++){
                &error($text{'keyspace_replicationerr'}) if($replication_factors[$i] == 0 || $replication_factors[$i] =~ /\D/);
                $replications = $replications." '$datacenters[$i]' : $replication_factors[$i],";
        }
	chop($replications);

	my $c = `$config{'cql_command'} -e "ALTER KEYSPACE $keyspace WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy',$replications } AND DURABLE_WRITES = $durable_writes;" 2>&1`;

	&error($c) if($?);

}

sub drop_keyspace
{
	my($keyspace_name)=@_;
	&error($text{'keyspacedrop_notexisterr'}) if(not (&is_keyspace_exists($keyspace_name)));
	my $c = `$config{'cql_command'} -e "Drop keyspace $keyspace_name;" 2>&1`;
	&error($c) if($?);
}

sub drop_udt
{
	my($keyspace,$udt)=@_;
	&error($text{'keyspacedrop_notexisterr'}) if(not (&is_keyspace_exists($keyspace)));
	my $c = `$config{'cql_command'} -e "DROP TYPE $keyspace.$udt;" 2>&1`;
	&error($c) if($?);	
}

sub drop_table
{
	my($keyspace,$table)=@_;
	&error($text{'keyspacedrop_notexisterr'}) if(not (&is_keyspace_exists($keyspace)));
	&error($text{'tabledrop_notexisterr'}) if(not (&is_table_exists($keyspace,$table)));
	my $c = `$config{'cql_command'} -e "DROP TABLE $keyspace.$table;" 2>&1`;
	&error($c) if($?);
}

sub drop_column
{
	my($keyspace,$table,$column)=@_;
	&error($text{'keyspacedrop_notexisterr'}) if(not (&is_keyspace_exists($keyspace)));
        &error($text{'tabledrop_notexisterr'}) if(not (&is_table_exists($keyspace,$table)));
	my $c=`$config{'cql_command'} -e "ALTER TABLE $keyspace.$table DROP $column;" 2>&1`;
	&error($c) if($?);
}

sub truncate_table
{
	my($keyspace,$table)=@_;
	&error($text{'tabletruncate_notexisterr'}) if(not (&is_table_exists($keyspace,$table)));
	my $c = `$config{'cql_command'} -e "TRUNCATE TABLE $keyspace.$table;" 2>&1`;
	&error($c) if($?);
}

sub get_keyspace_list
{
        my $keyspaces_cql = `$config{'cql_command'} -e "SELECT * FROM system_schema.keyspaces;" | tail -n +4 | head -n -2`;
        my @keyspaces = split(/\n/, $keyspaces_cql);
        my @infos = ();
        for my $keyspace(@keyspaces){
                my @keyspace_data = split(/\|/,$keyspace);
                my $strategy="";
		my @keyspace_data = grep(s/ //g, @keyspace_data);
		
		if(index($keyspace_data[2],"SimpleStrategy")!=-1){
			$strategy=$text{'keyspace_simplestrategy'};
		}elsif(index($keyspace_data[2],"LocalStrategy")!=-1){
			$strategy=$text{'keyspace_localstrategy'};
		}else{
			$strategy=$text{'keyspace_networktopologystrategy'};
		}
                push(@infos,{
                                "name" => $keyspace_data[0],
                                "replication_factor" => $keyspace_data[2],
                                "durable_writes" => $keyspace_data[1],
				"strategy" => $strategy
                        });
        }
        return @infos;
}



sub list_keyspaces
{
	my @keyspaces=&get_keyspace_list();		
	print &ui_columns_start([
			$text{'keyspace_list_name'},
			$text{'keyspace_strategy'},
			$text{'keyspace_list_delete'},
			$text{'keyspace_list_edit'}
				],"100%");
	foreach my $keyspace(@keyspaces){
		print &ui_columns_row(
			[ "<center>$keyspace->{'name'}</center>","<center>$keyspace->{'strategy'}</center>", "<a href='ask.cgi?type=keyspacedelete&keyspace=".&urlize($keyspace->{'name'})."'><center>".&ui_submit($text{'keyspace_list_delete'}) ."</center> </a>","<a href='edit_keyspace.cgi?keyspace=".&urlize($keyspace->{'name'})."'><center>".&ui_submit($text{'keyspace_list_edit'}) ."</center> </a>" ],100,0,\@tds);	

}
	print &ui_columns_end();
}

sub get_keyspace_info
{
	my $keyspace_name=shift;
	my $cql = `$config{'cql_command'} -e "SELECT * FROM system_schema.keyspaces WHERE keyspace_name='$keyspace_name';" | tail -n +4 | head -n -2`;
	$cql=~s/ |{|}|'//g;
	@data=split(/\|/,$cql);
	my $keyspace_name=$data[0];
	my $durable_writes=$data[1];
	my $replications=$data[2];
	my @replications=split(/,/,$replications);
	my %keyspace_data = (
		"name" => $keyspace_name,
		"durable_writes" => $durable_writes
	);

	my $datacenters="";
	my $replication_factors="";
	for my $i(@replications){
		my @data = split(/:/,$i);
		$data[0]=~s/\n//g;
		$data[1]=~s/\n//g;
		$keyspace_data{$data[0]}=$data[1];
		if($data[0] ne "durable_writes" && $data[0] ne "class" && $data[0] ne "name"){
			$datacenters = $datacenters . "$data[0],";
			$replication_factors = $replication_factors . "$data[1],";
		}	


	if(index($keyspace_data{'class'},"SimpleStrategy") != -1){
		$keyspace_data{'strategy'}="SimpleStrategy";
	}elsif(index($keyspace_data{'class'},"LocalTopology") != -1){
		$keyspace_data{'strategy'}="LocalStrategy";
	}else{
		chop($datacenters);
		chop($replication_factors);
		$keyspace_data{'strategy'}="NetworkTopologyStrategy";
		$keyspace_data{'datacenters'}=$datacenters;
		$keyspace_data{'replication_factors'}=$replication_factors;
	}

	}
	return %keyspace_data;
}


sub alter_simples_keyspace
{
	my($keyspace,$replication_factor,$durable_writes,$new_strategy,$old_strategy)=@_;
	&error($text{'keyspace_nameerr'}) if(not ($keyspace));
	&error($text{'keyspace_durablewriteserr'}) if($durable_writes ne "True" && $durable_writes ne "False");
	&error($text{'keyspace_replicationerr'}) if($replication_factor == 0 || $replication_factor =~ /\D/);

	my $c = `$config{'cql_command'} -e "ALTER KEYSPACE $keyspace WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : $replication_factor } AND DURABLE_WRITES = $durable_writes"; 2>&1`;

	&error($c) if ($?);
}

sub ui_datatype_selector
{
	my ($keyspace,$column)=@_;
	my @datatypes=&get_datatypes($keyspace);
	my $field="";
	$field=$field . "<input type=hidden id=datatype_$column name=datatype_$column value='ascii'>";
	$field=$field . "<select name=type_$column onchange=\"document.getElementById('datatype_$column').value=this.value\">";
	foreach my $type(@datatypes){
		$field=$field . "<option value=$type>$type</option>";
	}
	$field= $field . "</select> $text{'or'} ";
	$field= $field . "<input type=text name=type_$column value='' onchange=\"document.getElementById('datatype_$column').value=this.value\" >";

	return $field;
}

sub table_list{
	my($keyspace)=shift;
	my $cql=`$config{'cql_command'} -e "SELECT * FROM system_schema.tables WHERE keyspace_name = '$keyspace'" | tail -n +4 | head -n -2`;
	$cql =~ s/ //g;
	my @tables = split(/\n/,$cql);
	my $count = @tables;
	print &ui_table_start($text{'tablelist_header'},"width=100%", 3);
	if($count == 0){
		print "$text{'tablelist_notable'}";
	}else{
		print &ui_columns_start([
				$text{'tablelist_name'},
				$text{'tablelist_comment'},
				$text{'tablelist_delete'},
				$text{'tablelist_truncate'},
				$text{'tablelist_edit'}
			], "100%");

		foreach my $table(@tables){
			my @table_datas=split(/\|/,$table);
			print &ui_columns_row(
				[ "<center>$table_datas[1]</center>","$table_datas[6]","<a href='ask.cgi?type=tabledelete&keyspace=".&urlize($table_datas[0])."&table=".&urlize($table_datas[1])."'><center>".&ui_submit($text{'tablelist_delete'})."</a></center>","<a href='ask.cgi?type=tabletruncate&keyspace=".&urlize($table_datas[0])."&table=".&urlize($table_datas[1])."'><center>".&ui_submit($text{'tablelist_truncate'})."</a></center>","<a href='edit_table.cgi?keyspace=".&urlize($table_datas[0])."&table=".&urlize($table_datas[1])."'><center>".&ui_submit($text{'tablelist_edit'})."</a></center>"]);
		}
		print &ui_columns_end();
	}
	print &ui_table_end();
}

sub list_table_columns
{
	my($keyspace,$table)=@_;
	&error($text{'keyspace_edit_keyspacenotexist'}) if(not &is_keyspace_exists($keyspace));
        &error($text{'tabletruncate_notexisterr'}) if(not &is_table_exists($keyspace,$table));
	my @columns = &get_table_columns($keyspace,$table);
	print &ui_table_start(&text("tableedit_columns",$table));
	print &ui_columns_start([
			$text{'tableedit_columnname'},
			$text{'tableedit_datatype'},
			$text{'tableedit_kind'},
			$text{'tableedit_deletecolumn'}
		], "100%");

	foreach my $column(@columns){
		print &ui_columns_row(
			[ "$column->{'name'}","$column->{'datatype'}","$column->{'kind'}","<a href='ask.cgi?type=columndrop&keyspace=".&urlize($keyspace)."&table=".&urlize($table)."&column=".&urlize($column->{'name'})."'>".&ui_submit($text{'tableedit_deletecolumn'})."</a>" ]);
	}
	print &ui_columns_end();
	print &ui_table_end();


}
	


sub get_table_columns
{
	my($keyspace,$table)=@_;
	&error($text{'keyspace_edit_keyspacenotexist'}) if(not &is_keyspace_exists($keyspace));
	&error($text{'tabletruncate_notexisterr'}) if(not &is_table_exists($keyspace,$table));
	my $c=`$config{'cql_command'} -e "SELECT column_name,type,kind FROM system_schema.columns WHERE keyspace_name='$keyspace' AND table_name='$table';" | tail -n +4 | head -n -2`;
	&error($c) if($?);
	$c=~s/ //g;
	my @data=split(/\n/,$c);
	my @columns=();
	foreach my $col(@data){
		my @info = split(/\|/,$col);
		my $column = {
			'name' => $info[0],
			'datatype' => $info[1],
			'kind' => $info[2]
		};
		push(@columns,$column);
	}
	return @columns;
}

sub get_udtypes
{
	my $keyspace=shift;
	my $c=`$config{'cql_command'} -e "SELECT * FROM system_schema.types WHERE keyspace_name='$keyspace'" | tail -n +4 | head -n -2 2>&1`;
	$c=~s/ //g;
	my @data=split(/\n/,$c);
	my @udttypes=();
	foreach my $type(@data){
		my @data=split(/\|/,$type);
		my $typename=$data[1];
		my $nameoftypes=$data[2];
		$nameoftypes=~s/\[|\]|'//g;
		my @names=split(/,/,$nameoftypes);
		my $datatypes=$data[3];
		$datatypes=~s/\[|\]|'//g;
		my @types=split(/,/,$datatypes);
		my $udtinfo = {
				"name" => $typename,
				"subtypes" => \@names,
				"subdatatypes" => \@types
		};
		push(@udttypes,$udtinfo);
	}
	return @udttypes;
}


sub get_datatypes
{
	my $keyspace=shift;
	my @udtypes=&get_udtypes($keyspace);
	my @datatypes = ( "ascii", "bigint", "blob", "boolean", "counter", "date", "decimal", "double", "duration", "float", "inet", "int", "smallint", "text", "time", "timestamp", "timeuudi", "tinyint", "uuid", "varchar", "varint" );
	foreach my $udt(@udtypes){
		push(@datatypes,$udt->{'name'});
	}
	return @datatypes;
}

sub createudt_list
{
	my($keyspace,$countoftypes,$name)=@_;
	&error($text{'keyspace_edit_keyspacenotexist'}) if(not &is_keyspace_exists($keyspace));
	&error($text{'createudt_counterr'}) if($countoftypes<1);
	my @datatypes=&get_datatypes($keyspace);
	print &ui_form_start("save_udt.cgi");
	print &ui_columns_start([
			$text{'createudt_list_name'},
			$text{'createudt_list_datatype'}
		]);
	for(my $i=0;$i<$countoftypes;$i++){
		print &ui_columns_row(
			[ &ui_textbox("typename_$i",""), &ui_select("datatype_$i","ascii", \@datatypes) ]
		);
	}

	print &ui_columns_end();
	print &ui_hidden("count",$countoftypes);
	print &ui_hidden("name",$name);
	print &ui_hidden("keyspace_name",$keyspace);
	print &ui_submit($text{'createudt_save'});
	print &ui_form_end();

}

sub create_table_columns{
	my($countoffields,$keyspace,$table)=@_;
	my @datatypes = &get_datatypes($keyspace);
	my @others = ("CLUSTERING ORDER BY","comment","speculative_retry","cdc","additional_write_policy","gc_grace_seconds","bloom_filter_fp_chance","default_time_to_live","compaction","compression","caching","memtable_flush_period_in_ms","read_repair");
	

	print &ui_form_start('save_table.cgi');
	

	print &ui_hidden_start("Columns","columns",1);
	print &ui_columns_start([
			$text{'createtable_columnname'},
			$text{'createtable_datatype'},
			$text{'createtable_static'}
		]);
	for(my $i=0;$i<$countoffields;$i++){
		print &ui_columns_row(
			[ &ui_textbox("column_$i",""),&ui_datatype_selector($keyspace,$i), &ui_checkbox("static_$i","yes",undef,0)]); 
		}
	print &ui_columns_row(
		[ $text{'createtable_isprimarykey'}, &ui_textbox("primarykey",""),"" ]
	);
	print &ui_columns_end();
	print &ui_hidden_end();

	print &ui_hidden_start($text{'createtable_otheroptions'},"others",0);
	
	print &ui_columns_start([
			$text{'createtable_option'},
			$text{'createtable_value'}
	]);

	foreach(@others){
		print &ui_columns_row(
			[ $_, &ui_textbox($_,"") ]
		);
	}
	print &ui_hidden("keyspace",$keyspace);
	print &ui_hidden("table",$table);
	print &ui_columns_end();
	print &ui_hidden_end();
	
	print "<br>";

	print &ui_hidden("fields",$countoffields);
	print &ui_hidden("keyspace_name",$keyspace);
	print &ui_hidden("table_name",$table);
	print &ui_submit($text{'createtable_createbutton'});
	print &ui_reset($text{'createtable_resetbutton'});
	print &ui_form_end();

}

sub add_columns_list
{
	my($countoffields,$keyspace,$table)=@_;
	my @datatypes = &get_datatypes($keyspace);

	print &ui_form_start('alter_table.cgi');

	print &ui_columns_start([
			$text{'createtable_columnname'},
			$text{'createtable_datatype'},
			$text{'createtable_static'}
		]);
	for(my $i=0;$i<$countoffields;$i++){
		print &ui_columns_row(
                        [ &ui_textbox("column_$i",""), &ui_datatype_selector($keyspace,$i),&ui_checkbox("static_$i","yes",undef,0) ]);

	
	}
	print &ui_hidden("keyspace",$in{'keyspace_name'});
	print &ui_hidden("fields",$in{'fields'});
	print &ui_hidden("table",$in{'table_name'});
	print &ui_columns_end();
	print &ui_submit($text{'tableedit_save'});
	print &ui_form_end();
}

sub get_table_options
{
	my($keyspace,$table)=@_;
	&error($text{'keyspace_edit_keyspacenotexist'}) if(not &is_keyspace_exists($keyspace));
        &error($text{'tabletruncate_notexisterr'}) if(not &is_table_exists($keyspace,$table));
	my $c=`$config{'cql_command'} -e "DESC $keyspace.$table;" 2>&1`;
	chop($c);
	chop($c);
	my @datas=split(/WITH/,$c);
	my @options=split(/AND/,$datas[1]);
	my @optionslist=();
	my $check=0;
	foreach(@options){
		my $option="";
		my $value="";
		if (index($_,"CLUSTERING ORDER BY (") != -1){
			$_ =~ s/CLUSTERING ORDER BY //g;
			$option="CLUSTERING ORDER BY";
			$value=$_;
			$value=~ s/^\s+|\s+$//g;
			$value=substr($value,1);
			chop($value);
			$check=1;
		}else{
			my @data=split(/=/,$_);
			$option=$data[0];
			$value=$data[1];
			$option =~ s/^\s+|\s+$//g;
			$value =~ s/^\s+|\s+$//g;
			my $firstchar=substr($value,0,1);
			#if($firstchar eq "'"){
				#$value=substr($value,1);
				#chop($value);
				#}
		}
		my $o = {
                                'option' => $option,
                                'value' => $value
                };
		push(@optionslist,$o);
	}
		if (not $check){
			push(@optionslist,{
					'option' => "CLUSTERING ORDER BY",
					'value' => ""
			});
		}
	
	return @optionslist;		
}

1;
