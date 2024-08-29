#!/bin/sh

page=$1

second() {
number=$((1 + RANDOM % "${page}"))
echo "${number}"
second_link="https://creators.deepfake.com/popular/${number}"
second_pattern='https://creators.deepfake.com[^<]+'
second_request=$(curl -s -A "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" --location --max-time 30 "${second_link}" | grep -oP "${second_pattern}" | grep 'post' | sed 's/">/ /g')
IFS=$' '
for line in ${second_request}
do 
echo "${line}"
done
}

second ${page}

