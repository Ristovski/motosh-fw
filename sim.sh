#!/usr/bin/env sh

set -e

# Remove FW just in case, for now.
cd sim && FW=fw/$1 renode customfw.resc && rm fw/$1