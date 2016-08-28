#!/bin/bash
# Exit on first error
set -e

# Parse our CLI arguments
version="$1"
if test "$version" = ""; then
  echo "Expected a version to be provided to \`release.sh\` but none was provided." 1>&2
  echo "Usage: $0 [version] # (e.g. $0 1.0.0)" 1>&2
  exit 1
fi

# Verify release notes exist
if ! grep "## $version\$" changelog.md &> /dev/null; then
  echo "Expected \`changelog.md\` to contain \`## $version\` but it didn't. Please add release notes to \`changelog.md\`" 1>&2
  exit 1
fi

# Commit any pending changes
git commit -a -m "Release $version"

# Tag the release
git tag "$version"

# Publish the release to GitHub
git push
git push --tags
