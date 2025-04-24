#!/usr/bin/env bash
# wait-for-it.sh: wait until a TCP host:port is available
# Usage: wait-for-it.sh host:port [-t timeout] -- command args

set -e

HOST_PORT="$1"
shift

HOST="${HOST_PORT%%:*}"
PORT="${HOST_PORT##*:}"

TIMEOUT=60
while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

for ((i=0;i<TIMEOUT;i++)); do
  if nc -z "$HOST" "$PORT"; then
    exec "$@"
    exit 0
  fi
  sleep 1
done

>&2 echo "Timeout waiting for $HOST:$PORT"
exit 1
