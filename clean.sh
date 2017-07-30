#!/bin/bash

read -r -p "Are you sure? [Y/n] " response
case "$response" in
	[yY][eE][sS]|[yY])
		rm -v -f ./wav/*
		rm -v -f *.log
		;;
	*)
		echo "Aborting..."
		;;
esac
