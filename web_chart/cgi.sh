#!/bin/sh

set -eu

logfile='/home/pi/src/bsec_bme680_linux/log.csv'
n_logfile=0
n_readings="${QUERY_STRING}"
max_readings=100
m=0
out=''

# check if GET is int
printf "%s\n" "${n_readings}" \
| egrep -q '^[0-9]+$' >/dev/null

# Check how many readings log file has.
# Override n_readings if it's too large.
# Take off 1 for first line in a CSV.
n_logfile=$(
  wc -l "${logfile}" | cut -d ' ' -f 1
)
n_logfile=$((
  ${n_logfile} - 1
))

if [ "${n_readings}" -gt "${n_logfile}" ]; then
  n_readings=${n_logfile}
fi

# Greeting
printf "%s\n" 'Content-Type: text/plain; charset=utf-8'
printf "%s\n\n" 'Access-Control-Allow-Origin: *'

# Get the readings
readings="$(
  /usr/bin/tail -n "${n_readings}" "${logfile}"
)"

# If we got more readings than $max_readings allows, skip some in between
if [ "${n_readings}" -gt "${max_readings}" ]; then
  m=$(( ${n_readings} / ${max_readings} ))
  out="$(
    printf "%s\n" "${readings}" \
    | /usr/bin/awk "NR == 1 || NR % ${m} == 0"
  )"
else
  out="${readings}"
fi

printf "%s\n" "${out}"

exit

