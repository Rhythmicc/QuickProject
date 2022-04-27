zsh_comp_template = """#compdef __proj_name__

local cur prev
cur=${words[CURRENT]}
prev=${words[CURRENT-1]}

(( $+functions[___proj_name___args_comp] )) || 
___proj_name___args_comp() {
    local -a opt_args
    __sub_commands_args__
    _describe subcommand opt_args
}

(( $+functions[___proj_name___main] )) || 
___proj_name___main() {
    local -a args
    args=(
        __sub_commands__
    )

    _describe -t common-commands 'common commands' args && _ret=0
}

if (( ${#words} >= 3 )); then
    ___proj_name___args_comp
else
    ___proj_name___main
fi
"""
