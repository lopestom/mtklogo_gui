#!/usr/bin/env bash
# shellcheck disable=SC2059   # messages (lang/*.sh) are printf formats on purpose
# mtklogos.sh (v2.2) - interactive front-end for mtklogo (MediaTek logo.bin)
#
# Credits / base:
#   cyberknight777/mtklogo (binary and source) · arlept/mtklogo (original)
#   Sakurajima07 / 4pda (original script) · lopestom (upstream binary-source code improvements)
#
# What changed versus v1 (see ANALYSIS_AND_SUGGESTIONS.md):
#   * no recursion (v1 called ./mtklogos.sh from inside `select`);
#   * profiles come from mtklogo.yaml (`mtklogo profiles`): a new profile shows up
#     in the menu by itself, no script edit needed;
#   * "Detect profile" tests every profile with --no-out and ranks them;
#   * separate folders: logo/ (unpack), explore/, out/ (results), backup/ (original, once);
#   * no more copying the binary into logo/ (that broke repack);
#   * the output file name is the one the message reports;
#   * validates the width, asks before deleting/overwriting;
#   * with the patched mtklogo it uses --reference (checks dimensions and size).
#   * v2.2: multi-image containers (logo1 + logo2 + ... in one logo.bin, e.g. Android 16): with a
#     mtklogo that has `unpack --image`, `split` and `join`, every image is unpacked into its own
#     sub-folder of logo/ and repacked + joined back; older binaries behave exactly as before.
#     The .mtklogo-meta file is moved to the /backup folder for safety during the Repack process.
#     Fixed a Repack error related by @Rusikxxx about multi-image.
#   * v2.1: messages in lang/<code>.sh (en, pt, de, es, fr, ru). The language follows
#     MTKLOGO_GUI_LANG, LANGUAGE, LC_ALL, LC_MESSAGES, LANG (English if unknown).
#
# Usage:  ./mtklogos.sh            (LOGO_BIN=other.bin ./mtklogos.sh for another file)

PS3='#? '                       # select prompt (the GUI recognises "#? ")
cd "$(dirname "$(readlink -f "$0")")" || exit 1

LOGO_BIN="${LOGO_BIN:-logo.bin}"
UNPACK_DIR="logo"
EXPLORE_DIR="explore"
OUT_DIR="out"
BACKUP_DIR="backup"
STATE_FILE=".mtklogos_state"

# ---- language ------------------------------------------------------------------
LANG_DIRS=("$PWD/lang" "$PWD/../lang")

find_lang_file() {   # find_lang_file <code> -> prints the path of <code>.sh
    local d; for d in "${LANG_DIRS[@]}"; do [ -f "$d/$1.sh" ] && { echo "$d/$1.sh"; return 0; }; done; return 1
}

pick_lang() {        # first requested language that has a file; English otherwise
    local v val c base IFS=:
    for v in MTKLOGO_GUI_LANG LANGUAGE LC_ALL LC_MESSAGES LANG; do
        val="${!v:-}"; [ -n "$val" ] || continue
        for c in $val; do
            base="${c%%[._@]*}"; base="${base%%-*}"; base="${base,,}"
            case "$base" in c|posix|en|"") echo en; return;; esac
            find_lang_file "$base" >/dev/null && { echo "$base"; return; }
        done
    done
    echo en
}

# shellcheck disable=SC1090
{ f=$(find_lang_file en) && . "$f"; }                          # defaults (English)
# shellcheck disable=SC1090
{ SCRIPT_LANG=$(pick_lang); [ "$SCRIPT_LANG" != en ] && f=$(find_lang_file "$SCRIPT_LANG") && . "$f"; }

C1=$'\033[1;36m'; C2=$'\033[1;34m'; CW=$'\033[1;33m'; CE=$'\033[1;31m'; C0=$'\033[0m'
fmt()    { local f="$1"; shift; printf "$f" "$@"; }
say()    { fmt "$@"; echo; }
banner() { echo -e "${C1} ************************************************* ${C0}"
           for l in "$@"; do echo -e "${C2}   $l ${C0}"; done
           echo -e "${C1} ************************************************* ${C0}"; }
warn()   { echo -e "${CW}${P_WARN}${C0} $*"; }
err()    { echo -e "${CE}${P_ERR}${C0} $*"; }

# ---- locate mtklogo ----------------------------------------------------------
chmod u+x ./mtklogo 2>/dev/null
if [ -x ./mtklogo ]; then MTKLOGO=./mtklogo
elif command -v mtklogo >/dev/null 2>&1; then MTKLOGO=$(command -v mtklogo)
else err "$(fmt "$M_NO_BIN" "$PWD")"; exit 1; fi
say "$M_USING" "$MTKLOGO" "$PWD"

HAS_PROFILES=0; HAS_REFERENCE=0; HAS_IMAGE=0
"$MTKLOGO" profiles >/dev/null 2>&1 && HAS_PROFILES=1
"$MTKLOGO" repack --help 2>/dev/null | grep -q -- '--reference' && HAS_REFERENCE=1
"$MTKLOGO" unpack --help 2>/dev/null | grep -q -- '--image' && HAS_IMAGE=1

# ---- helpers -----------------------------------------------------------------
strip_ansi() { sed -E 's/\x1b\[[0-9;]*[A-Za-z]//g'; }

confirm() {   # confirm "question" -> 0 if yes; default = no (y/s/j/o and the full words)
    local a; printf '%s %s ' "$1" "$Y_HINT"; read -r a || return 1
    case "${a,,}" in y|yes|s|sim|si|sí|j|ja|o|oui|д|да|Д|Да|ДА) return 0;; *) return 1;; esac
}

ask() {       # ask "question" -> answer in $REPLY
    printf '%s ' "$1"; read -r REPLY || exit 0
}

list_profiles() {   # lines: name<TAB>model<TAB>number of formats<TAB>aliases
    if [ "$HAS_PROFILES" = 1 ]; then "$MTKLOGO" profiles
    else   # fallback without the subcommand: read the names straight from the yaml
        local y; for y in "$HOME/.config/mtklogo.yaml" /etc/mtklogo.yaml ./mtklogo.yaml; do [ -f "$y" ] && break; done
        sed -nE 's/^[[:space:]]*-[[:space:]]+name:[[:space:]]*([^[:space:]#]+).*/\1\t?\t?\t/p' "$y"
    fi
}

choose_profile() {  # pick a profile -> $PROFILE (empty if cancelled)
    local -a names labels; local n cm cnt al i
    while IFS=$'\t' read -r n cm cnt al; do
        names+=("$n"); labels+=("$n  [$cm, $cnt $W_FORMATS${al:+, $W_ALIAS: $al}]")
    done < <(list_profiles)
    [ ${#names[@]} -eq 0 ] && { err "$M_NO_PROFILES"; PROFILE=""; return 1; }
    echo; echo "  $M_WHICH"
    select _ in "${labels[@]}" "$M_CANCEL"; do
        [ -z "${REPLY:-}" ] && continue
        if [ "$REPLY" -eq $(( ${#names[@]} + 1 )) ] 2>/dev/null; then PROFILE=""; return 1; fi
        i=$(( REPLY - 1 ))
        if [ "$i" -ge 0 ] && [ "$i" -lt ${#names[@]} ]; then PROFILE="${names[$i]}"; return 0; fi
        echo "  $M_INVALID_OPT"
    done
    PROFILE=""; return 1
}

need_logo_bin() {
    [ -f "$LOGO_BIN" ] && return 0
    banner "$(fmt "$M_NO_LOGO" "$LOGO_BIN" "$PWD")" "$M_PUT_LOGO"
    return 1
}

IMAGES=1
count_images() {  # sets IMAGES = number of logo images inside $LOGO_BIN (always 1 without `--image` support)
    IMAGES=1
    { [ "$HAS_IMAGE" = 1 ] && [ -f "$LOGO_BIN" ]; } || return 0
    local tmp n; tmp=$(mktemp -d)
    n=$("$MTKLOGO" split -o "$tmp" "$LOGO_BIN" 2>&1 | strip_ansi | grep -c '^image [0-9]')
    rm -rf -- "$tmp"
    [ "${n:-0}" -ge 1 ] && IMAGES=$n
}

make_backup() {   # single copy of the original logo.bin
    mkdir -p "$BACKUP_DIR"
    if [ ! -e "$BACKUP_DIR/$(basename "$LOGO_BIN").orig" ]; then
        cp -p -- "$LOGO_BIN" "$BACKUP_DIR/$(basename "$LOGO_BIN").orig" &&
            say "$M_BACKUP" "$BACKUP_DIR/$(basename "$LOGO_BIN").orig"
    fi
}

clean_dir() {     # empties one of the work folders (fixed names, never arbitrary paths)
    local d="$1"
    case "$d" in "$UNPACK_DIR"|"$EXPLORE_DIR") ;; *) err "$(fmt "$M_DIR_BAD" "$d")"; return 1;; esac
    if [ -d "$d" ] && [ -n "$(ls -A -- "$d" 2>/dev/null)" ]; then
        confirm "$(fmt "$M_DIR_ASK" "$d")" || return 1
        find "$d" -mindepth 1 -delete
    fi
    mkdir -p "$d"
}

# ---- actions -------------------------------------------------------------------
do_unpack() {
    need_logo_bin || return
    choose_profile || { echo "$M_CANCELLED"; return; }
    clean_dir "$UNPACK_DIR" || { echo "$M_CANCELLED"; return; }
    make_backup
    say "$M_PROFILE_SEL" "$PROFILE"
    count_images
    local -a imgopt=()
    if [ "$IMAGES" -gt 1 ]; then imgopt=(--image all); say "$M_MULTI" "$IMAGES"; fi
    "$MTKLOGO" unpack -p "$PROFILE" "${imgopt[@]}" "$LOGO_BIN" -o "$UNPACK_DIR" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$'
    local rc=${PIPESTATUS[0]} raw png
    echo "$PROFILE" > "$STATE_FILE"
    [ "$rc" -eq 0 ] && [ "$IMAGES" -gt 1 ] && save_parts
    shopt -s nullglob
    local -a _z=("$UNPACK_DIR"/*raw.z "$UNPACK_DIR"/*/*raw.z) _p=("$UNPACK_DIR"/*.png "$UNPACK_DIR"/*/*.png)
    shopt -u nullglob
    raw=${#_z[@]}; png=${#_p[@]}
    if [ "$rc" -ne 0 ]; then err "$(fmt "$M_UNPACK_RC" "$rc")"; return; fi
    banner "$(fmt "$M_UNPACK_T" "$PROFILE")" "$(fmt "$M_UNPACK_PNG" "$png" "$UNPACK_DIR")" "$(fmt "$M_UNPACK_RAW" "$raw")"
    [ "$raw" -gt 0 ] && warn "$M_RAW_HINT"
}

save_parts() {
    # keeps each original image (reference for repack) and the container order
    local d="$UNPACK_DIR/.parts"
    mkdir -p "$d"
    "$MTKLOGO" split -o "$d" "$LOGO_BIN" 2>&1 | strip_ansi \
        | sed -nE 's#.*[/\\]([^/]+)\.bin$#\1#p' > "$d/order"
}

do_detect() {
    need_logo_bin || return
    echo "$M_DET_START"
    local n cm cnt al out ok total best="" bestok=-1 tmp bin lbin
    local -a rows imgopt=()
    count_images; [ "$IMAGES" -gt 1 ] && imgopt=(--image all)
    # -n writes a .mtklogo-meta into the current folder: run in a temporary one
    tmp=$(mktemp -d); bin=$(readlink -f "$MTKLOGO"); lbin=$(readlink -f "$LOGO_BIN")
    while IFS=$'\t' read -r n cm cnt al; do
        out=$(cd "$tmp" && "$bin" unpack -n -p "$n" "${imgopt[@]}" "$lbin" 2>&1 | strip_ansi)
        ok=$(grep -c 'will be exported as' <<<"$out")
        total=$(sed -nE 's/.*logo image has ([0-9]+).*/\1/p' <<<"$out" | awk '{s+=$1} END{print s+0}')
        rows+=("$ok|$total|$n")
        if [ "$ok" -gt "$bestok" ]; then bestok=$ok; best=$n; fi
    done < <(list_profiles)
    rm -rf -- "$tmp"
    echo; echo "$M_DET_HDR"
    printf '%s\n' "${rows[@]}" | sort -t'|' -k1,1nr | head -8 | while IFS='|' read -r ok total n; do
        printf '        %3s / %-3s              %s\n' "$ok" "${total:-?}" "$n"; done
    echo
    if [ "$bestok" -le 0 ]; then warn "$M_DET_NONE"; return; fi
    say "$M_DET_BEST" "$best" "$bestok"
    warn "$M_DET_TIE"
    if confirm "$(fmt "$M_DET_ASK" "$best")"; then
        PROFILE="$best"; clean_dir "$UNPACK_DIR" || return; make_backup
        "$MTKLOGO" unpack -p "$PROFILE" "${imgopt[@]}" "$LOGO_BIN" -o "$UNPACK_DIR" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$' | tail -3
        echo "$PROFILE" > "$STATE_FILE"
        [ "$IMAGES" -gt 1 ] && save_parts
    fi
}

do_explore() {
    need_logo_bin || return
    local w s
    while :; do
        ask "$M_ASK_W"; w="$REPLY"
        [ -z "$w" ] && { echo "$M_CANCELLED"; return; }
        [[ "$w" =~ ^[0-9]+$ ]] && [ "$w" -ge 16 ] && [ "$w" -le 10000 ] && break
        echo "$M_BAD_W"
    done
    ask "$M_ASK_S"; s="${REPLY:-0}"
    [[ "$s" =~ ^[0-9]+([,-][0-9]+)*$ ]] || { err "$(fmt "$M_BAD_S" "$s")"; return; }
    clean_dir "$EXPLORE_DIR" || { echo "$M_CANCELLED"; return; }
    make_backup
    "$MTKLOGO" explore "$LOGO_BIN" --slots "$s" --width "$w" -o "$EXPLORE_DIR" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$'
    banner "$(fmt "$M_EXP_T" "$EXPLORE_DIR")" "$M_EXP_1" "$M_EXP_2"
    say "$M_EXP_NEXT" "$w"
}

_meta_to_backup() {   # _meta_to_backup <srcdir>...   -> move .mtklogo-meta to $BACKUP_DIR (overwrites)
    local d
    for d in "$@"; do
        [ -n "$d" ] && [ -f "$d/.mtklogo-meta" ] || continue
        mkdir -p -- "$BACKUP_DIR"
        mv -f -- "$d/.mtklogo-meta" "$BACKUP_DIR/.mtklogo-meta"
    done
}

do_repack() {
    local dir="${1:-$UNPACK_DIR}" prof="" out files alpha=() ref=()
    [ -f "$STATE_FILE" ] && prof=$(<"$STATE_FILE")
    [ -d "$dir" ] || { err "$(fmt "$M_NO_DIR" "$dir")"; return; }
    _meta_to_backup "$dir"                      # <<< move before the repack
    if [ -s "$dir/.parts/order" ]; then do_repack_multi "$dir" "$prof"; return; fi
    shopt -s nullglob; files=("$dir"/logo_*); shopt -u nullglob
    [ ${#files[@]} -eq 0 ] && { err "$(fmt "$M_NO_FILES" "$dir")"; return; }
    say "$M_N_FILES" "${#files[@]}" "$dir"
    confirm "$M_ALPHA" && alpha=(--alpha)
    mkdir -p "$OUT_DIR"
    out="$OUT_DIR/logo_${prof:-custom}_$(date +%Y%m%d-%H%M%S).bin"
    if [ "$HAS_REFERENCE" = 1 ] && [ -f "$LOGO_BIN" ]; then ref=(--reference "$LOGO_BIN"); fi
    "$MTKLOGO" repack "${alpha[@]}" "${ref[@]}" "${files[@]}" -o "$out" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$' | grep -v ' is slot [0-9]* in '
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
        if [ "$HAS_REFERENCE" = 1 ] && confirm "$M_FORCE"; then
            "$MTKLOGO" repack "${alpha[@]}" "${ref[@]}" --force "${files[@]}" -o "$out" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$' | grep -v ' is slot [0-9]* in '
            [ "${PIPESTATUS[0]}" -ne 0 ] && { err "$M_RP_FAIL"; rm -f -- "$out"; return; }
        else
            err "$M_RP_NOT"; rm -f -- "$out"; return
        fi
    fi
    banner "$(fmt "$M_RP_DONE" "$out")" "$(fmt "$M_RP_SIZE" "$(du -b -- "$out" | cut -f1)" "$(sha256sum -- "$out" | cut -c1-16)")"
    warn "$M_RP_WARN"
}

repack_one() {    # repack_one <out> <reference|""> <file>...   (reads $alpha of the caller) -> 0 = ok
    local out="$1" refp="$2"; shift 2
    local -a ref=()
    { [ "$HAS_REFERENCE" = 1 ] && [ -n "$refp" ] && [ -f "$refp" ]; } && ref=(--reference "$refp")
    "$MTKLOGO" repack "${alpha[@]}" "${ref[@]}" "$@" -o "$out" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$' | grep -v ' is slot [0-9]* in '
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
        if [ "${#ref[@]}" -gt 0 ] && confirm "$M_FORCE"; then
            "$MTKLOGO" repack "${alpha[@]}" "${ref[@]}" --force "$@" -o "$out" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$' | grep -v ' is slot [0-9]* in '
            [ "${PIPESTATUS[0]}" -ne 0 ] && { err "$M_RP_FAIL"; rm -f -- "$out"; return 1; }
        else
            err "$M_RP_NOT"; rm -f -- "$out"; return 1
        fi
    fi
    return 0
}

do_repack_multi() {   # several logo images: repack every sub-folder, then join them in container order
    local dir="$1" prof="$2" out tmp name sub
    local -a alpha=() parts=() order files
    mapfile -t order < "$dir/.parts/order"
    say "$M_MULTI_RP" "${#order[@]}"
    confirm "$M_ALPHA" && alpha=(--alpha)
    mkdir -p "$OUT_DIR"
    out="$OUT_DIR/logo_${prof:-custom}_$(date +%Y%m%d-%H%M%S).bin"
    tmp=$(mktemp -d)
    for name in "${order[@]}"; do
        sub="$dir/$name"
        shopt -s nullglob; files=("$sub"/logo_*); shopt -u nullglob
        [ ${#files[@]} -eq 0 ] && { err "$(fmt "$M_NO_FILES" "$sub")"; rm -rf -- "$tmp"; return; }
        _meta_to_backup "$sub"                  # <<< move before the repack multi images (overwrites)
        say "$M_N_FILES" "${#files[@]}" "$sub"
        repack_one "$tmp/$name.bin" "$dir/.parts/$name.bin" "${files[@]}" || { rm -rf -- "$tmp"; return; }
        parts+=("$tmp/$name.bin")
    done
    "$MTKLOGO" join -o "$out" "${parts[@]}" 2>&1 | strip_ansi | grep -v '░' | grep -v '^$'
    [ "${PIPESTATUS[0]}" -ne 0 ] && { err "$M_JOIN_FAIL"; rm -f -- "$out"; rm -rf -- "$tmp"; return; }
    rm -rf -- "$tmp"
    banner "$(fmt "$M_RP_DONE" "$out")" "$(fmt "$M_RP_SIZE" "$(du -b -- "$out" | cut -f1)" "$(sha256sum -- "$out" | cut -c1-16)")"
    warn "$M_RP_WARN"
}

do_repack_other() {
    ask "$(fmt "$M_ASK_DIR" "$UNPACK_DIR")"
    local d="${REPLY:-$UNPACK_DIR}"
    [ -d "$d" ] || { err "$(fmt "$M_DIR_NF" "$d")"; return; }
    do_repack "$d"
}

do_profiles() {
    echo; printf '  %-22s %-9s %-9s %s\n' "$W_PROFILE" "$W_MODEL" "$W_FORMATS_U" "$W_ALIAS_U"
    list_profiles | while IFS=$'\t' read -r n cm cnt al; do printf '  %-22s %-9s %-9s %s\n' "$n" "$cm" "$cnt" "$al"; done
}

# ---- main loop (no recursion) ----------------------------------------------------
echo "mtklogo $ENG_VERSION"
echo "$M_TIP"
while :; do
    echo
    select action in "$M_MENU_1" "$M_MENU_2" "$M_MENU_3" "$M_MENU_4" "$M_MENU_5" "$M_MENU_6" "$M_MENU_7"; do
        case "$REPLY" in
            1) do_unpack ;;
            2) do_detect ;;
            3) do_repack ;;
            4) do_explore ;;
            5) do_repack_other ;;
            6) do_profiles ;;
            7) echo "$M_EXITING"; exit 0 ;;
            *) echo "$M_INVALID_OPT"; continue ;;
        esac
        break        # leave select so the menu is printed again
    done || exit 0
done
