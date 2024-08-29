#!/bin/sh

cmd='curl -s -A "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" --location --max-time 30'

first() {
first_link="https://creators.deepfake.com/popular"
first_pattern='Last Page[^<]+'
first_request=$(${cmd} "${first_link}" | grep -oP "${first_pattern}" | grep -oP '">...[^<]+' | sed 's/">...//g')
IFS=$'\n'
for line in $(echo "${first_request}")
do 
  echo "${line}"
  break
done
}

first

