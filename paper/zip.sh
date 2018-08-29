#! /usr/bin/env bash
#
# The ACM requires that we submit the source code of our paper along with the
# paper itself. This script zips up all of our source code. Navigate to the
# wat/paper directory and then run the script:
#
#   $ cd wat/paper
#   $ ./zip.sh
#
# This will create a 187-whittaker.zip file that includes all the relevant
# files in the repository.

set -euo pipefail

main() {
    # Check that we're in the wat/paper directory.
    if [[ "$(basename $PWD)" != "paper" ]]; then
        echo "Please run this script in the wat/paper directory." 1>&2;
        exit 1
    fi

    # Remove garbage that we don't want in the zip file, including the existing
    # zip file.
    latexmk -C
    rm -f "187-whittaker.zip"
    rm -f "187-whittaker.bbl"
    rm -f "comment.cut"

    # Create the zip file.
    zip -r "187-whittaker.zip" .
}

main "$@"
