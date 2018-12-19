#!/bin/bash
ping -c 1 google.com
if [ "$?" != "0" ]; then

