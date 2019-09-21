#!/bin/bash

# escribid los scripts para que los tabuladores los convierta en 4 espacios.

# inicializaciones de paths, imprescindibles
# las variables de entorno son generadas por rgbux-env
. /opt/RGBux/bin/system-base

# contiene funciones de ayuda, como los replace
. /opt/RGBux/bin/rgbux-helpers


# DATA BASE
DATA_FILE=$HOME/.mame/mame.ini
DATA_VAR="autosave"
DEFAULT_VALUE="disabled"

function runcmd()
{
    value=$1 # cambiar enabled por 1
    if [ "$value" = "enabled" ]; then
        replace_mame $DATA_VAR 1 $DATA_FILE
        echo "SAVESTATES: ENABLED!"
    else
        replace_mame $DATA_VAR $DEFAULT_VALUE $DATA_FILE
        echo "SAVESTATES: DISABLED!"
    fi

}

function print_opts()
{
    echo "$DEFAULT_VALUE|enabled"
}

function print_current()
{
    current=$(get_mame $DATA_VAR $DATA_FILE)
    case $current in
        1)
            echo "enabled"
            ;;
        "")
            _install_value
            ;;
        *)
            echo "$DEFAULT_VALUE"
            ;;
    esac
}

function _install_value()
{
    echo -e "\n$DATA_VAR         $DEFAULT_VALUE\n" >> $DATA_FILE
}

case $1 in
    current)
        print_current
        ;;
    info)
        print_opts
        ;;
    run)
        runcmd $2
        ;;
    *)
        echo "$0: [run|info|current]"
        ;;
esac

