#!/bin/bash

n="0"

while [[ $n -lt 10 ]]
do
  echo "All work and no play makes Jane a dull girl" >/dev/stdout
  sleep 2 
  n=$[$n + 1]
done
echo "Fail!" >/dev/stderr
exit 2