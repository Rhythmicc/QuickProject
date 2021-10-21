complete -F _qrun_complete_func qrun
_qrun_complete_func() {
    command_name="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=(
        $(compgen -W "-b -r -br -if -f -h *" -- ${command_name}),
        $(compgen -G "*" -- ${command_name})
    )
    return 0
}
