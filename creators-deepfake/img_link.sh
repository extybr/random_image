#!/bin/sh

link=$1
cmd='curl -s -A "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" --location --max-time 30'

third() {
#echo $link
third_pattern='https://deepfake0001.s3.amazonaws.com/wowify/[^<]+'
third_request=$(${cmd} "${link}" | grep -oP "${third_pattern}" | sed 's/" class="img-fluid lazyload d-inline-block" title=//g')
echo "${third_request}"
}

third ${link}

