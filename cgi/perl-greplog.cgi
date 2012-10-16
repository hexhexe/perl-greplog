#!/usr/bin/perl

#############################
# PGL (Perl Grep Logviewer) #
#                           #
# written by: Lucy Pelzer   #
# license: GPL              #
#                           #
# last update: 2012/10/08   #
#############################


#
# needed modules
#
use strict;
use Template;
use CGI;
use File::Basename;
use File::ReadBackwards;
use HTML::Entities; 

#
# variable defination
#
my $cgi = CGI->new;
my %logs = ();
my $search_mask = "!/^\./";
my @log_files = ();
my @content = ();
my @reverse_content = ();
my $current_revert = HTML::Entities::encode($cgi->param('revert'));
my $line = "";
my $line_counter = 0;
my $log_file = HTML::Entities::decode($cgi->param('log_file'));
my $max_lines = 50;
my $http_vars = ();
my $css = "";
my $meta = "";
my $regexp = "";
my $webpath = "cgi-bin";
my $csspath ="css_docs";
my $count = 0;
my $refresh_secs = 30;
my $encoded_regexp = "";
my %css_files = (
     "perl-greplog-dark.css" => "black",
     "perl-greplog-orange.css" => "orange",
     "perl-greplog-light.css" => "white",
);


#
# reading config file in /etc/perl-greplog.conf
#
open CFG, "/etc/perl-greplog.conf" or die "Can not read config file";
while (<CFG>) {
    chomp;
  if ($_ =~ /^\s*$/  ||  $_ =~ /^#/) 
  {
    next;
  }
  my ($key, $value) = split (/\s*=\s*/, $_);
  if ($key eq "logs") 
  {
    for my $log (split (/\s*,\s*/, $value))
    {
      $logs{$log} = 1
    }
  } elsif ($key eq "max_lines")
  { 
    $max_lines = $value;
  } elsif ($key eq "css")
  {
    $css = $value;
  } elsif ($key eq "dir_search_mask") 
  {
    $search_mask = $value;
  } elsif ($key eq "webpath")
  {
    $webpath = $value;
  } elsif ($key eq "csspath")
  {
    $csspath = $value;
  } elsif ($key eq "refresh_sec")
  {
    $refresh_secs = $value;
  } elsif ($key eq "css_file")
  {
    my ($k, $v) = split (/\s*:\s*/, $value);
    $css_files{$k} = $v;
  }
}
close CFG;


#
# build the log_files list
#

#for each elemets in logs
foreach my $log (keys %logs)
{
  # check if the entry is a file 
  if ( -f "$log") 
  {
    # check if the file could be read
    if (-r "$log") 
    {
      # put the file into the array log_files
      push @log_files, $log;
    } else 
    {
      print STDERR "No permission to read the logfile $log !"; 
    }
  } else 
  { 
    # open a directory reader
    opendir(DIR,"$log") || die "Cannot read dir $log\n$!\n";
    # for all entrys in the directory 
    foreach my $dir_content (grep { $search_mask } readdir(DIR))
    {
      # check if it is a file and it is readable
      if (-r "$log/$dir_content" && -f  "$log/$dir_content")
      {
        # and put it into the array log_files
        push @log_files, $log."/".$dir_content;
      }
    }
    # close the directory reader
    closedir(DIR);
  }
}

#
# check for parmaterws in the request
#

# check if there is a linenumber parameter
if ($cgi->param('linenumber')) {
  # if there is something else than numbers in the string max_lines ...
  if ($cgi->param('linenumber') =~ /\D/)
  {
    # log the injection
    print STDERR "Someone injected the linenumber parameter!";
  } else 
  {
     $max_lines = $cgi->param('linenumber');
  }
}

# check if there is a css file parameter
if ($cgi->param ('css_files'))
{
  # if the css_file is allowed to be used
  if( $css_files { $cgi->param('css_files')})
  {
    # set it as css
    $css = $cgi->param('css_files');
  } else
  {
    # log the injection
    print STDERR "Someone injected the css_files parameter!"   
  }
}


#
# main programm
#

#set the html content type if there is NO cgi parameter download
if (!$cgi->param('download'))
{
  # needed from the webserver to communicate with the html template                                                              
  print "Content-type: text/html\r\n\r\n";
}


#
# main logic
#

# check if there is a parameter log_file in the request
if ($cgi->param("log_file"))
{
  # check if the logfile is allowed to be viewed
  if( $log_file ~~  @log_files )
  {
    # if the button search has been presst
    if ($cgi->param('show'))
    {
      #search to the log backwards
      backwards_search_file ();
    # if the button download has been presst
    } elsif ($cgi->param('download'))
    {
      # dwonload the file
      download_file ();
    }
  # there must have been an injection 
  } else
  {
      print STDERR "The logfile parameter has been injected!";
      empty_start ();
  }
# empty start page
} else
{
    empty_start ();
}


# open a TemplateToolkit to send variables to the html
my $TemplateToolkit = Template->new(
{  
  INCLUDE_PATH => '.',
  INTERPOLATE => 1,    
} ) || die "failed to create templateToolkit" .  "$Template::ERROR\n";


#
# set the html meta tag
#

# if the checkbox tail is checked and the show button refresh the website every x sec
if ($cgi->param('tail')  && $cgi->param('show'))
{
  if ($cgi->param('tail') eq "tail")
  {
  # set the meta data to reload the page every x secounds 
  $meta = '<meta http-equiv="Content-type" content="text/html; charset=utf-8" /> ' . '<meta http-equiv="refresh" content="' . $refresh_secs . '; url=/' . $webpath . '/perl-greplog.cgi?show=1&amp;log_file=' . HTML::Entities::encode($log_file) . '&amp;linenumber=' . $max_lines . '&amp;revert=' . $current_revert . '&amp;css_files=' . $css . '&amp;regexp=' . HTML::Entities::encode($cgi->param('regexp')) . '&amp;colors=' . HTML::Entities::encode($cgi->param('colors')) . '&amp;tail=tail&amp;csspath=' . $csspath . '" />';
  # Parameter tail has been injected
  } else
  {        
    $meta = '<meta http-equiv="Content-type" content="text/html; charset=utf-8" />';
    print STDERR "There may have been a injection in the tail parameter";
  }
} else
{
  # else set the default meta data 
  $meta = '<meta http-equiv="Content-type" content="text/html; charset=utf-8" />';
}


#
# prepare the replay parameters
#
$http_vars = {
  log_files => \@log_files,
  content => \@content,
  csspath => $csspath,
  webpath => $webpath,
  current_log_file => HTML::Entities::encode($log_file),
  current_revert => $current_revert,
  current_search_regexp => HTML::Entities::encode($cgi->param('regexp')),
  current_linenumber => $max_lines,
  css_files => \%css_files,
  current_colors => HTML::Entities::encode($cgi->param('colors')),
  current_css => $css,
  current_meta => $meta,
  current_tail => $cgi->param('tail'),
};

#
# send the replay
#
$TemplateToolkit->process(
  'perl-greplog.html', $http_vars
) || die "failed to give variables to templateToolkit" . $TemplateToolkit->error(), "\n";




#
# functions
#

#
# empty start page
#
sub empty_start ()
{
  #set the html content type if there is a download parameter
  if ($cgi->param('download'))
  {
    # needed from the webserver to communicate with the html template
    print "Content-type: text/html\r\n\r\n";
  }
  $current_revert = "revert";
}


#
# opens the file backwards and reads max_line number (the log could be also showen in normal order when revert is not set)
#
sub backwards_search_file ()
{
  # put the loglines in reverse order  into the variable line (last logsed first out)
  eval 
  {
    # open a backwards file reader
    my $br = File::ReadBackwards->new ($log_file)or die "Can not read" . $log_file . ": $!\n"; 

    READLINES: while( defined($line = $br->readline ) ) 
    {
      # check if there is a parameter regexp in the Post from the browser
      if ($cgi->param('regexp'))
      {
        # if there is a regexp only print lines with regex
	search_regexp ();
      # if there is no regexp in the Post put all lines into the content array 
      }else {
        $line_counter++;
        push @content, HTML::Entities::encode($line);
      }
      # if there is a new line in the content try to color it
      if ($line_counter > $count) 
      {
        # do not color or set hrefs if the download button has been pressed
        if (!$cgi->param('download'))
        {
	  href_color_output ();
        }
      }
      # stop to fill the content when there are max_lines in the content
      if ($line_counter == $max_lines) 
      {
       last READLINES;
      }
    }
  };  
  # if the eval produces an error there must be an error in the regexp
  if ($@)
  {
    print STDERR $@;
    # so just print as content the following line
    push @content, "Please quote your regexp!";
  }
  # check if there is NO parameter revert                                                      
  if (!$cgi->param('revert')) 
  {
    # show the file in the normal format
    @content = reverse(@content);
  }
}
# END backword read file

#
# function search regexp
#
sub search_regexp ()
{
  # check if the regexp is in the logline and... 
  $regexp = HTML::Entities::decode($cgi->param("regexp"));
  if($line =~ /$regexp/i)
  {
    $line_counter++;
    # put it into the content array
    push @content, HTML::Entities::encode($line);
  }
}

#
# function to color regex and make urls to links 
#
sub href_color_output () 
{
  # html encode the regexp to prevent injection
  $encoded_regexp = HTML::Entities::encode($cgi->param('regexp'));

  # if there is an url in the content
  if ($content[-1] =~ /(((ht|f)tp(s?))\:\/\/.*?)(\s|")/)
  {
    my $link = $1;
    # split the content to color the parts left and right from a url 
    my @split = split ( /(.*?)(((ht|f)tp(s?))\:\/\/.*?)([\s|"].*$)/,$content[-1]);
    my $prelink = @split[1];
    my $postlink = @split[6];
    $link =~ s/\&quot;$//i;
    # only color the hrefs and the regexp if the checkbox colors is checked
    if ( $cgi->param('colors'))
    {
      # make it to a colored href
      $link = '<a class="color_url" href="' . $link .'">' . $link . '</a>';
      # if ther is a regexp ...
      if ( $cgi->param('regexp'))
      {
        # color it before and after the hyperlink
        $prelink =~ s/$regexp/\<a class="regexp"\> $encoded_regexp \<\/a\>/ig;
        $postlink =~ s/$regexp/\<a class="regexp"\> $encoded_regexp \<\/a\>/ig;
      }
    # if the checkbox colors is not checked ...
    } else
    {
      # only make the hyperlink
      $link = '<a class="url" href="' . $link .'">' . $link . '</a>';
    }
    # put the content together again
    $content[-1] = $prelink . $link . $postlink;
  # if there is no href but a regexp and the checkbox colors is checked
  } elsif ( $cgi->param('regexp') && $cgi->param('colors'))
  {
    # color it
    $content[-1] =~ s/$regexp/\<a class="regexp"\>$encoded_regexp\<\/a\>/g;
  }
  # increment the content by 1;
  $count++;
}


# download stuff
sub download_file () 
{
  # needed by the webserver to init a download
  print "Content-Type:application/x-download\n";
  print "Content-Disposition:attachment;filename=" . $log_file ."\n\n";

  # if there are search parameters prepare the file before the download  
  if ($cgi->param('regexp') || $cgi->param('linenumber') || $cgi->param('revert') ){
      backwards_search_file ();
  } else
  {
    # log what logfile has been downloaded          
    print STDERR "Downloaded file" . $log_file;
    # open the whole file for the download 
    open( FILE, "<" . $log_file) || Error('open', 'file');
    @content  =  <FILE>;
    close(FILE) || Error ('close', 'file');
  }
  # start the download dialog
  print @content;
  exit 1;
}

#
# download error message
#
sub Error ()
{
  print "Content-type: text/html\n\n";
  print "The server can't $_[0] the $_[1]: $! \n";
  exit;                                                                                                                            
}

#
# script has to return 1 to the webserver if everything is good
#
1;
