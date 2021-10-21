_qrun(){
    local cur cword words
    read -cn cword
    read -Ac words
    cur="${words[$cword-1]}"
    if [ "$cur" = "qrun" ]; then
        reply=(-b -r -br -h -f -if $(qrun --qrun-commander-complete))
    else
        reply=(*)
    fi
}

_Qpro() {
    local cur cword words
    read -cn cword
    read -Ac words
    cur="${words[$cword-1]}"
    if [ "$cur" = "Qpro" ]; then
        reply=(-init -h -c -update -adjust -ssh -scp -scp-init -get -del -del-all -ls)
    else
        reply=(*)
    fi
}

compctl -K _qrun qrun
compctl -K _Qpro Qpro
