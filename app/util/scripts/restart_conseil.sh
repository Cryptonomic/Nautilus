#!/bin/bash

docker start "conseil-lorre-$1"

docker start "conseil-api-$1"