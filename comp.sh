complete -F _qrun_complete_func qrun
complete -F _Qpro_complete_func Qpro
_qrun_complete_func() {
    command_name="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=(
        $(compgen -W "-b -r -br -if -f -h" -- ${command_name})
        $(compgen -C "qrun --complete" -- ${command_name})
        $(compgen -G "*" -- ${command_name})
    )
    return 0
}

_Qpro_complete_func() {
    command_name="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=(
        $(compgen -W "-init -h -c -update -adjust -ssh -scp -scp-init -get -del -del-all -ls" -- "${command_name}")
        $(compgen -G "*" -- "${command_name}")
    )
}
