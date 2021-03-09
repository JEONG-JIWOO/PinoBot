#! /bin/bash

# Check if run in root
if [ "$EUID" -ne 0 ]
  then echo "ERROR: Run with sudo command"
  exit
fi

RANDOM_FRONT=$(printf %03d $(( $RANDOM % 1000 )))
RANDOM_BACK=$(printf %04d $(( $RANDOM % 10000 )))
NEW_HOST_NAME="p$RANDOM_FRONT$RANDOM_BACK"
hostnamectl set-hostname $NEW_HOST_NAME