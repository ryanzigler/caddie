#!/usr/bin/env bash
# SessionStart hook, and the janitor it starts.
# Test harnesses and probes leave scratch directories in /tmp that nobody removes.
# On the Railway container the kernel's file and dentry caches for them are
# billed as memory (175k leftover directories once added ~5 GB to the bill), and
# the cache cannot be dropped from inside the container, so deleting the files
# is the only lever. This keeps one low-priority janitor per user that deletes
# stale top-level entries of /tmp.
#
#   temp-janitor.sh            hook: start the janitor if none is running, print nothing
#   temp-janitor.sh --daemon   the janitor loop (a trailing state path only labels it in ps)
#   temp-janitor.sh --once     one pass, then exit
#
# Off unless CADDIE_TEMP_JANITOR=1, or RAILWAY_SERVICE_ID is set and
# CADDIE_TEMP_JANITOR is not 0. README.md documents every variable.

# Names in the temp directory that are never deleted. Entries are shell globs.
KEEP_NAMES=(
  "claude-$(id -u)" # Claude Code task outputs and tool results for live sessions
  "cc-socks"        # Claude Code session sockets
  "tsx-$(id -u)"    # tsx compile cache
)

DEFAULT_ROOTS=(/tmp /private/tmp)
DEFAULT_MAX_AGE=2h
DEFAULT_INTERVAL=10m
MIN_MAX_AGE_SECONDS=600
DELETE_BATCH=200
LOG_MAX_BYTES=262144

enabled() {
  case "${CADDIE_TEMP_JANITOR:-}" in
    1|true|on|yes) return 0 ;;
    0|false|off|no) return 1 ;;
  esac
  [ -n "${RAILWAY_SERVICE_ID:-}" ]
}

state_dir() {
  if [ -n "${CADDIE_TEMP_JANITOR_STATE_DIR:-}" ]; then
    printf '%s\n' "$CADDIE_TEMP_JANITOR_STATE_DIR"
  elif [ -n "${XDG_STATE_HOME:-}" ]; then
    printf '%s\n' "$XDG_STATE_HOME/caddie/temp-janitor"
  elif [ -n "${HOME:-}" ]; then
    printf '%s\n' "$HOME/.local/state/caddie/temp-janitor"
  else
    return 1
  fi
}

script_path() {
  local dir
  dir="$(cd -P "$(dirname "$0")" && pwd -P)" || return 1
  printf '%s/%s\n' "$dir" "$(basename "$0")"
}

log() {
  local size
  if [ -f "$LOG" ]; then
    size="$(wc -c <"$LOG")"
    [ "${size// /}" -gt "$LOG_MAX_BYTES" ] && mv -f "$LOG" "$LOG.1"
  fi
  printf '%s pid=%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$$" "$*" >>"$LOG"
}

# "90m", "2h", "30s", or bare minutes, in seconds.
duration_seconds() {
  [[ "$1" =~ ^([0-9]{1,6})([smh]?)$ ]] || return 1
  local number="$((10#${BASH_REMATCH[1]}))"
  case "${BASH_REMATCH[2]}" in
    s) printf '%s\n' "$number" ;;
    h) printf '%s\n' "$((number * 3600))" ;;
    *) printf '%s\n' "$((number * 60))" ;;
  esac
}

is_under() {
  local path="$1" parent="$2"
  [ "$path" = "$parent" ] || case "$path" in "${parent%/}"/*) return 0 ;; *) return 1 ;; esac
}

resolve_dir() {
  [ -d "$1" ] && (cd -P "$1" 2>/dev/null && pwd -P)
}

# Prints the resolved temp directory, or explains on stderr why it refuses.
resolve_root() {
  local root candidate home volume parent inside=""
  if [ -n "${CADDIE_TEMP_JANITOR_TEST_ROOT:-}" ]; then
    root="$(resolve_dir "$CADDIE_TEMP_JANITOR_TEST_ROOT")" || {
      echo "test root $CADDIE_TEMP_JANITOR_TEST_ROOT is not a directory" >&2
      return 1
    }
    # A test root is a fixture inside a temp directory, never one itself.
    for parent in /tmp "${TMPDIR:-/tmp}"; do
      parent="$(resolve_dir "$parent")" || continue
      [ "$root" != "$parent" ] && is_under "$root" "$parent" && inside=1
    done
    [ -n "$inside" ] || { echo "test root $root is not inside /tmp or \$TMPDIR" >&2; return 1; }
  else
    root="$(resolve_dir /tmp)" || { echo "/tmp is not a directory" >&2; return 1; }
    for candidate in "${DEFAULT_ROOTS[@]}"; do
      [ "$root" = "$candidate" ] && break
      candidate=""
    done
    [ -n "$candidate" ] || { echo "/tmp resolves to unexpected $root" >&2; return 1; }
  fi

  case "$root" in
    /|/bin|/boot|/dev|/etc|/home|/lib*|/opt|/proc|/root|/run|/sbin|/srv|/sys|/usr|/var|/Users|/System|/Library|/Applications|/private|/private/var)
      echo "refusing system directory $root" >&2
      return 1 ;;
  esac
  if [ -n "${HOME:-}" ]; then
    home="$(resolve_dir "$HOME" || printf '%s' "$HOME")"
    if is_under "$root" "$home" || is_under "$home" "$root"; then
      echo "refusing $root: it overlaps the home directory $home" >&2
      return 1
    fi
  fi
  for volume in "${RAILWAY_VOLUME_MOUNT_PATH:-}" /data; do
    [ -n "$volume" ] || continue
    volume="$(resolve_dir "$volume" || printf '%s' "$volume")"
    if is_under "$root" "$volume" || is_under "$volume" "$root"; then
      echo "refusing $root: it overlaps the persistent volume $volume" >&2
      return 1
    fi
    # A volume mounted at the root shares its device even when the paths differ.
    if [ -d "$volume" ] && [ "$(device_of "$volume")" = "$(device_of "$root")" ]; then
      echo "refusing $root: it is on the same filesystem as the persistent volume $volume" >&2
      return 1
    fi
  done
  printf '%s\n' "$root"
}

# The janitor's own process, not an unrelated one that reused its pid.
holder_alive() {
  local pid="$1" cmd
  case "$pid" in ''|*[!0-9]*) return 1 ;; esac
  kill -0 "$pid" 2>/dev/null || return 1
  if [ -r "/proc/$pid/cmdline" ]; then
    cmd="$(tr '\0' ' ' <"/proc/$pid/cmdline" 2>/dev/null)"
  else
    cmd="$(ps -p "$pid" -o command= 2>/dev/null)"
  fi
  case "$cmd" in *temp-janitor.sh*--daemon*|*temp-janitor.sh*--once*) return 0 ;; *) return 1 ;; esac
}

# The lock is a file holding the holder's pid, created with `ln`, which is
# atomic and fails when the file exists. Taking over a dead holder's lock is
# serialized by a takeover directory so two starters cannot both win.
acquire_lock() {
  local mine="$STATE/lock.$$" holder
  printf '%s\n' "$$" >"$mine" || return 1
  for _ in 1 2 3; do
    if ln "$mine" "$LOCK" 2>/dev/null; then
      rm -f "$mine"
      return 0
    fi
    holder="$(head -n 1 "$LOCK" 2>/dev/null)"
    # Gone or mid-takeover: try the link again rather than treat it as dead.
    [ -n "$holder" ] || continue
    if holder_alive "$holder"; then
      rm -f "$mine"
      return 1
    fi
    if mkdir "$STATE/takeover" 2>/dev/null; then
      if [ "$(head -n 1 "$LOCK" 2>/dev/null)" = "$holder" ] && ! holder_alive "$holder"; then
        rm -f "$LOCK"
      fi
      rmdir "$STATE/takeover"
    else
      if [ -n "$(find "$STATE/takeover" -maxdepth 0 -mmin +1 2>/dev/null)" ]; then
        rmdir "$STATE/takeover" 2>/dev/null
      fi
      sleep 1
    fi
  done
  rm -f "$mine"
  return 1
}

owns_lock() {
  [ "$(head -n 1 "$LOCK" 2>/dev/null)" = "$$" ]
}

stat_devices() {
  if stat -c %d / >/dev/null 2>&1; then
    tr '\n' '\0' | xargs -0 stat -c '%d %n' 2>/dev/null
  else
    tr '\n' '\0' | xargs -0 stat -f '%d %N' 2>/dev/null
  fi
}

device_of() {
  printf '%s\n' "$1" | stat_devices | cut -d ' ' -f 1
}

# Every path a live process has as its working directory, executable, open
# file, or memory mapping. /proc on Linux, lsof elsewhere.
open_paths() {
  if [ -d /proc/self/fd ] && find /proc/self/cwd -maxdepth 0 -printf '' 2>/dev/null; then
    find /proc/[0-9]*/cwd /proc/[0-9]*/exe /proc/[0-9]*/fd -maxdepth 1 -printf '%l\n' 2>/dev/null
    cat /proc/[0-9]*/maps 2>/dev/null | awk '{ i = index($0, "/"); if (i) print substr($0, i) }'
  elif command -v lsof >/dev/null 2>&1; then
    lsof -w -n -P -F n 2>/dev/null | sed -n 's/^n//p'
  fi
}

under_root() {
  awk -v prefix="$ROOT/" '{ print prefix $0 }'
}

# Top-level names under $ROOT that the paths on stdin point into.
top_names() {
  awk -v prefix="$ROOT/" 'index($0, prefix) == 1 {
    name = substr($0, length(prefix) + 1)
    sub(/\/.*/, "", name)
    sub(/ \(deleted\)$/, "", name)
    if (name != "" && !(name in seen)) { seen[name] = 1; print name }
  }'
}

# Top-level names in use by a live process, into $1. Fails when the scan
# cannot see this process's own working directory, because then it cannot be
# trusted to see anyone else's.
scan_in_use() {
  open_paths >"$WORK/open"
  grep -qFx "$STATE" "$WORK/open" || return 1
  top_names <"$WORK/open" >"$1"
}

# Moves names on stdin that are not listed in $1 to stdout.
without() {
  if [ -s "$1" ]; then grep -vFx -f "$1"; else cat; fi
}

reference_time() {
  local epoch="$1" stamp
  stamp="$(date -d "@$epoch" +%Y%m%d%H%M.%S 2>/dev/null || date -r "$epoch" +%Y%m%d%H%M.%S 2>/dev/null)" || return 1
  touch -t "$stamp" "$WORK/reference"
}

count_entries() {
  find "$ROOT" -mindepth 1 -maxdepth 1 -print0 2>/dev/null | tr -dc '\0' | wc -c | tr -d ' '
}

run_pass() {
  local started uid name pattern keep line dev path in_use fresh removed=0 failed=0 batch=() total extra=()
  read -r -a extra <<<"${CADDIE_TEMP_JANITOR_KEEP//,/ }"
  started="$(date +%s)"
  uid="$(id -u)"
  WORK="$(mktemp -d "$STATE/pass.XXXXXX")" || { log "pass skipped: cannot create a work directory in $STATE"; return; }

  reference_time "$((started - MAX_AGE_SECONDS))" || { log "pass skipped: cannot create the age reference"; rm -rf "$WORK"; return; }

  # Old top-level entries we own, never a symlink or a socket.
  find "$ROOT" -mindepth 1 -maxdepth 1 -user "$uid" ! -type l ! -type s \
    ! -newermm "$WORK/reference" ! -newercm "$WORK/reference" -print0 2>/dev/null |
    while IFS= read -r -d '' path; do
      name="${path#"$ROOT"/}"
      case "$name" in ''|.|..|*/*|*$'\n'*) continue ;; esac
      keep=0
      for pattern in "${KEEP_NAMES[@]}" ${extra[@]+"${extra[@]}"}; do
        case "$name" in $pattern) keep=1; break ;; esac
      done
      [ "$keep" = 1 ] || printf '%s\n' "$name"
    done >"$WORK/old"

  # Same filesystem as the root: a mount point is someone else's.
  under_root <"$WORK/old" | stat_devices | while IFS= read -r line; do
    dev="${line%% *}"
    path="${line#* }"
    [ "$dev" = "$ROOT_DEV" ] && printf '%s\n' "${path#"$ROOT"/}"
  done >"$WORK/local"

  # A live process's working directory, open file, or mapping.
  if ! scan_in_use "$WORK/in-use"; then
    log "pass skipped: cannot see open files or working directories of live processes (no /proc and no lsof)"
    rm -rf "$WORK"
    return
  fi
  without "$WORK/in-use" <"$WORK/local" >"$WORK/idle"

  # Anything inside modified recently, owned by another user, or a socket.
  : >"$WORK/busy"
  if [ -s "$WORK/idle" ]; then
    under_root <"$WORK/idle" | tr '\n' '\0' |
      xargs -0 sh -c 'ref="$1" uid="$2"; shift 2; find "$@" -xdev -mindepth 1 \( -newermm "$ref" -o -newercm "$ref" -o ! -user "$uid" -o -type s \) -print 2>/dev/null' sh "$WORK/reference" "$uid" |
      top_names >"$WORK/busy"
  fi
  without "$WORK/busy" <"$WORK/idle" >"$WORK/doomed"

  in_use="$(($(wc -l <"$WORK/local") - $(wc -l <"$WORK/idle")))"
  fresh="$(($(wc -l <"$WORK/idle") - $(wc -l <"$WORK/doomed")))"
  total="$(wc -l <"$WORK/doomed" | tr -d ' ')"

  if [ "$DRY_RUN" = 1 ]; then
    head -n 100 "$WORK/doomed" | while IFS= read -r name; do log "dry-run would remove $ROOT/$name"; done
    [ "$total" -gt 100 ] && log "dry-run would remove $((total - 100)) more"
    log "pass dry_run=1 root=$ROOT would_remove=$total kept=$(count_entries) in_use=$in_use busy_inside=$fresh secs=$(($(date +%s) - started))"
    rm -rf "$WORK"
    return
  fi

  # Minutes can pass between the checks above and a late batch, so each batch
  # first re-reads which entries are in use and re-checks type and owner.
  delete_batch() {
    local idle=() checked=()
    [ "${#batch[@]}" -gt 0 ] || return 0
    if ! scan_in_use "$WORK/in-use-now"; then
      failed=$((failed + ${#batch[@]}))
      batch=()
      return 0
    fi
    while IFS= read -r path; do
      idle+=("$path")
    done < <(printf '%s\n' "${batch[@]}" | without "$WORK/in-use-now" | under_root)
    if [ "${#idle[@]}" -gt 0 ]; then
      while IFS= read -r -d '' path; do
        case "${path#"$ROOT"/}" in ''|*/*) continue ;; esac
        checked+=("$path")
      done < <(find "${idle[@]}" -maxdepth 0 -user "$uid" ! -type l ! -type s -print0 2>/dev/null)
    fi
    in_use=$((in_use + ${#batch[@]} - ${#checked[@]}))
    if [ "${#checked[@]}" -gt 0 ]; then
      find "${checked[@]}" -xdev -delete 2>/dev/null
      for path in "${checked[@]}"; do
        if [ -e "$path" ] || [ -L "$path" ]; then failed=$((failed + 1)); else removed=$((removed + 1)); fi
      done
    fi
    batch=()
    sleep 0.2
  }
  while IFS= read -r name; do
    batch+=("$name")
    [ "${#batch[@]}" -ge "$DELETE_BATCH" ] && delete_batch
  done <"$WORK/doomed"
  delete_batch

  log "pass dry_run=0 root=$ROOT removed=$removed kept=$(count_entries) in_use=$in_use busy_inside=$fresh failed=$failed secs=$(($(date +%s) - started))"
  rm -rf "$WORK"
}

configure() {
  STATE="$(state_dir)" || return 1
  mkdir -p "$STATE" 2>/dev/null || return 1
  STATE="$(cd -P "$STATE" && pwd -P)" || return 1
  LOCK="$STATE/lock"
  LOG="$STATE/janitor.log"
  cd "$STATE" || return 1

  ROOT="$(resolve_root 2>"$STATE/refusal")" || { log "refusing to run: $(cat "$STATE/refusal")"; return 1; }
  rm -f "$STATE/refusal"
  if is_under "$STATE" "$ROOT"; then
    log "refusing to run: state directory $STATE is inside $ROOT"
    return 1
  fi
  ROOT_DEV="$(device_of "$ROOT")"
  [ -n "$ROOT_DEV" ] || { log "refusing to run: cannot read the device of $ROOT"; return 1; }

  MAX_AGE_SECONDS="$(duration_seconds "${CADDIE_TEMP_JANITOR_MAX_AGE:-$DEFAULT_MAX_AGE}")" || {
    log "refusing to run: CADDIE_TEMP_JANITOR_MAX_AGE=${CADDIE_TEMP_JANITOR_MAX_AGE} is not a duration like 90m or 2h"
    return 1
  }
  INTERVAL_SECONDS="$(duration_seconds "${CADDIE_TEMP_JANITOR_INTERVAL:-$DEFAULT_INTERVAL}")" || {
    log "refusing to run: CADDIE_TEMP_JANITOR_INTERVAL=${CADDIE_TEMP_JANITOR_INTERVAL} is not a duration like 10m"
    return 1
  }
  if [ "$MAX_AGE_SECONDS" -lt "$MIN_MAX_AGE_SECONDS" ] && [ -z "${CADDIE_TEMP_JANITOR_TEST_ROOT:-}" ]; then
    log "raising CADDIE_TEMP_JANITOR_MAX_AGE to the ${MIN_MAX_AGE_SECONDS}s minimum"
    MAX_AGE_SECONDS="$MIN_MAX_AGE_SECONDS"
  fi
  [ "$INTERVAL_SECONDS" -ge 1 ] || INTERVAL_SECONDS=1

  case "${CADDIE_TEMP_JANITOR_DRY_RUN:-}" in 1|true|on|yes) DRY_RUN=1 ;; *) DRY_RUN=0 ;; esac
}

lower_priority() {
  renice -n 19 -p "$$" >/dev/null 2>&1
  command -v ionice >/dev/null 2>&1 && ionice -c 3 -p "$$" >/dev/null 2>&1
  return 0
}

daemon() {
  local self sleeper=""
  enabled || exit 0
  configure || exit 0
  acquire_lock || exit 0
  self="$(script_path)"
  trap '[ -n "$sleeper" ] && kill "$sleeper" 2>/dev/null; owns_lock && rm -f "$LOCK"; log "stopped"; exit 0' TERM INT HUP
  rm -rf "$STATE"/pass.* 2>/dev/null
  lower_priority
  log "started root=$ROOT max_age=${MAX_AGE_SECONDS}s interval=${INTERVAL_SECONDS}s dry_run=$DRY_RUN"
  while :; do
    run_pass
    sleep "$INTERVAL_SECONDS" &
    sleeper=$!
    wait "$sleeper"
    sleeper=""
    # A newer janitor took the lock, or the plugin was updated or removed.
    owns_lock || { log "stopped: lock is held by another janitor"; exit 0; }
    [ -f "$self" ] || { log "stopped: $self no longer exists"; rm -f "$LOCK"; exit 0; }
  done
}

once() {
  enabled || { echo "temp-janitor: disabled; set CADDIE_TEMP_JANITOR=1 to run it" >&2; exit 1; }
  configure || { echo "temp-janitor: refused; see ${LOG:-the log}" >&2; exit 1; }
  if [ "$DRY_RUN" = 0 ]; then
    acquire_lock || { echo "temp-janitor: another janitor holds $LOCK" >&2; exit 1; }
    trap 'owns_lock && rm -f "$LOCK"' EXIT
  fi
  lower_priority
  run_pass
}

# SessionStart: never print, never fail, never wait.
hook() {
  local state self holder launcher=()
  enabled || return 0
  state="$(state_dir)" || return 0
  holder="$(head -n 1 "$state/lock" 2>/dev/null)"
  holder_alive "$holder" && return 0
  self="$(script_path)" || return 0
  command -v setsid >/dev/null 2>&1 && launcher=(setsid)
  nohup ${launcher[@]+"${launcher[@]}"} bash "$self" --daemon "$state" </dev/null >/dev/null 2>&1 &
}

main() {
  case "${1:-}" in
    --daemon) daemon ;;
    --once) once ;;
    *) hook >/dev/null 2>&1; exit 0 ;;
  esac
}

# Bash reads a script as it runs; parsing main first keeps a running janitor
# intact when the plugin is updated underneath it.
main "$@"
exit
