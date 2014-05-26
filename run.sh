#!/bin/bash

./python_play.test > /dev/null &
./python.test

killall -9 python_play.test


