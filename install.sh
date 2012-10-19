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
  install_dir="/srv/http/logviewer";
  echo "The install dir is: $install_dir"
fi

# install needed perl modules
cpan File::ReadBackwards;
cpan HTML::Entities;
cpan Template;
cpan HTML::Entities;

# if the perl version is below 5.016
if [ `perl -e "if ( $] < 5.016000) { print 'true';}"` ]; then
    cd cgi
    patch perl-greplog.cgi < perl-greplog.patch
    cd ..
fi


# create directorys
mkdir -p $install_dir/web > /dev/null 2>&1;
mkdir $install_dir/cgi-bin > /dev/null 2>&1;

# cp needed files
cp -v css/* $install_dir/web > /dev/null 2>&1;
cp -v cgi/* $install_dir/cgi-bin > /dev/null 2>&1;
cp -v conf/perl-greplog.conf /etc/> /dev/null 2>&1;

chown -R $user $install_dir;
chmod 0400 $install_dir/web/*;
chmod 0400 $install_dir/cgi-bin/perl-greplog.html;
chmod 0500 $install_dir/cgi-bin/perl-greplog.cgi;

echo ''
echo 'Installation finished successfull!'
echo ''
echo '# Put the following lines into you your apache config or virtual host config'
echo ''
echo '    #'
echo '    # logviewer configration'
echo '    #'
echo '    ScriptAlias /logviewer/ "'$install_dir'/cgi-bin/"'
echo '     <Location /logviewer>'
echo '        Options ExecCGI'
echo '        Order Deny,Allow'
echo '        Deny from all'
echo '        Allow from 192.168.0.0/16'
echo '     </Location>'
echo ''
echo '     Alias /css_docs/ "'$install_dir'/web/"'
echo '     <Directory /css_docs>'
echo '        Order Deny,Allow'
echo '        Deny from all'
echo '        Allow from 192.168.0.0/16'
echo '     </Directory>'
echo ''
echo '# Change the Allow Option to your IP frame or delete the lines'
echo ''
echo '# On some systems you need to add the following line in your httpd.conf to'
echo '# enable the apache cgi module'
echo ''
echo 'LoadModule cgi_module modules/mod_cgi.so'
echo ''
echo ' # If you change the ScriptAlias or the Alias don't forget'
echo ' # to change them in the config file /etc/perl-greplog.conf too'
