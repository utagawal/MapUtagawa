#!/bin/bash

cookiejar=$(mktemp cookies.XXXXXXXXXX)
netrc=$(mktemp netrc.XXXXXXXXXX)
chmod 0600 "$cookiejar" "$netrc"
function finish {
  rm -rf "$cookiejar" "$netrc"
}

trap finish EXIT

password_file=password.txt
if [ -f "$password_file" ]; then
    cat "$password_file" >> $netrc
else    
  echo "Enter your Earthdata Login ( https://urs.earthdata.nasa.gov/home ) "
  read -p "Username: " username
  read -s -p "Password: " password
  echo "machine urs.earthdata.nasa.gov login $username password $password" >> $netrc
  echo
  echo "Connect Earthdata ..."
fi

while read -r line;do
# Get everything after the last '/'

filename="$(dirname "${1}")/${line##*/}"
echo $line
curl -f -b "$cookiejar" -c "$cookiejar" -L --netrc-file "$netrc" -g -o $filename -- $line
unzip $filename -d $(dirname "${1}")
rm $filename
done < $1;

