#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="PiNetMonitor"
UPDATE_FEED_URL="${PINETMONITOR_UPDATE_FEED_URL:-https://raw.githubusercontent.com/agraja38/app-update-feeds/main/pinetmonitor/update.json}"

log() {
  echo "[${PROJECT_NAME}] $1"
}

require_root() {
  if [ "${EUID}" -ne 0 ]; then
    log "Please run the installer as root or with sudo."
    exit 1
  fi
}

main() {
  require_root

  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' EXIT

  log "Reading public update feed"
  curl -fsSL "$UPDATE_FEED_URL" -o "${tmp_dir}/update.json"
  package_url="$(sed -n 's/.*"packageURL"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "${tmp_dir}/update.json" | head -n 1)"

  if [ -z "$package_url" ]; then
    log "Public installs are not available yet because the feed does not contain a packageURL."
    log "Publish a PiNetMonitor release package to app-update-feeds, then rerun this installer."
    exit 1
  fi

  log "Downloading public release package"
  curl -fsSL "$package_url" -o "${tmp_dir}/pinetmonitor.tar.gz"
  mkdir -p "${tmp_dir}/package"
  tar -xzf "${tmp_dir}/pinetmonitor.tar.gz" -C "${tmp_dir}/package"

  installer="$(find "${tmp_dir}/package" -type f -path '*/scripts/install.sh' | head -n 1)"
  if [ -z "$installer" ]; then
    log "The public release package does not contain scripts/install.sh."
    exit 1
  fi

  chmod +x "$installer"
  "$installer"
}

main "$@"
