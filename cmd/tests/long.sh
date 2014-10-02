#!/bin/bash

n="0"

while [[ $n -lt 40 ]]
do
  echo "All work and no play makes Jack a dull boy" >/dev/stderr
  echo "All work and no play makes Jane a dull girl" >/dev/stdout
  sleep 2 
  n=$[$n + 1]

done