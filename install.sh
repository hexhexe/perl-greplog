#!/bin/bash

#############################
# PGL (Perl Grep Logviewer) #
#                           #
# written by: Lucy Pelzer   #
# license: GPL              #
#                           #
# last update: 2012/10/08   #
#############################

if [  $# -gt "0" ]; then
    user=$1;
else
    echo "You need to give the http user as fist parameter!"
    echo "USAGE: ./install.sh <username> <install_dir>"
    exit 1;
fi    

if [ $# -gt "1"  ]; then
   install_dir=$2;
   echo "The install dir is: $2"
else    
  install_dir="/srv/http";
  echo "The install dir is: $install_dir"
fi

# install needed perl modules
cpan File::ReadBackwards;
cpan HTML::Entities;
cpan Template;
cpan HTML::Entities;

# if the perl version is below 5.016
if [ `perl -e "if ( $] > 5.016000) { print 'true';}"` ]; then;
    cd cgi
    patch perl-greplog.cgi < perl-greplog.diff
    cd ..
fi;


# create directorys
mkdir -p $install_dir/css_files;
mkdir $install_dir/cgi_bin;

# cp needed files
cp css/* $install_dir/css_files;
cp cgi/* $install_dir/cgi_bin;
cp perl-greplog.conf /etc/;

chown -R $user $install_dir;
chmod 0400 $install_dir/css_files/*;
chmod 0400 $install_dir/cgi_bin/perl-greplog.html;
chmod 0500 $install_dir/cgi_bin/perl-greplog.cgi;

    #
    # enable the logviewer
    #
    # touch /var/www/logviewer/conf/
     ScriptAlias /logviewer/ "/var/www/logviewer/cgi-bin/"
     <Location /logviewer>
        Options ExecCGI 
        Order Deny,Allow
        Deny from all
        Allow from 172.16.0.220 Nagios
        Allow from 172.17.0.0/16
        Allow from 194.126.145.240
        Allow from 62.184.128.2
#        Authtype basic
#        AuthName "logviewer"
#       Require valid-user
     </Location>
    # if you change did directory you also need to change it in the htmlfile in the firstline at /var/www/logviewer/cgi-bin/perl-greplog
.html
     Alias /css_docs/ "/var/www/logviewer/css_docs/"
     <Directory /css_docs>
        Order Deny,Allow
        Deny from all
        Allow from 172.17.0.0/16
        Allow from 194.126.145.240
        Allow from 62.184.128.2
     </Directory>


