_qrun(){
    local cur cword words
    read -cn cword
    read -Ac words
    cur="${words[$cword-1]}"
    if [ "$cur" = "qrun" ]; then
        reply=(-b -r -br -h -f -if $(qrun --qrun-commander-complete))
    else
        prefix=$words[$cword]
        reply=(${prefix}* ${prefix}*/)
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
        prefix=$words[$cword]
        reply=(${prefix}* ${prefix}*/)
    fi
}

_detector() {
  local cur cword words
  read -cn cword
  read -Ac words
  cur="${words[$cword-1]}"
  if [ "$cur" = "detector" ]; then
      reply=(-pp -pf -fp -ff)
  else
      prefix=$words[$cword]
      reply=(${prefix}* ${prefix}*/)
  fi
}

_tmpm() {
  local cur cword words
  read -cn cword
  read -Ac words
  cur="${words[$cword-1]}"
  if [ "$cur" = "tmpm" ]; then
      reply=(-h -c -a -r -i *)
  elif [ "$cur" = "-c" ] || [ "$cur" = "-a" ]; then
      reply=($(tmpm -complete))
  else
      prefix=$words[$cword]
      reply=(${prefix}* ${prefix}*/)
  fi
}

compctl -K _qrun qrun
compctl -K _Qpro Qpro
compctl -K _detector detector
compctl -K _tmpm tmpm
