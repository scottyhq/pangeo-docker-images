# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/srv/conda/envs/pangeo/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/srv/conda/envs/pangeo/etc/profile.d/conda.sh" ]; then
        . "/srv/conda/envs/pangeo/etc/profile.d/conda.sh"
    else
        export PATH="/srv/conda/envs/pangeo/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
