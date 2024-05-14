#!/bin/bash

path="$1"; shift
docker run --rm -v $path:/out  ghcr.io/aborelis/asn-gen:latest  ./asn-gen.py $@ /out/