#! /bin/bash
declare -gA version action ver_index unlock_meta_token
ver_index["VERSION 2"]=3
ver_index["VERSION 3"]=5
unlock_meta_token="/var/run/disableMetaProtection.token"


skip_options ()
{
    while IFS= read -r line && [[ -n "$line" ]]
    do
        :
    done
}

if ! [ -f "${unlock_meta_token}" ];then

    IFS= read line
    case $line in
        "VERSION "[23])
            ver_index="${ver_index[$line]}"
            skip_options
            while read -ra pack
            do
                version["${pack[0]}"]="${pack[$ver_index]}"
                action["${pack[0]}"]="${pack[-1]}"
            done
            ;;
        *)
            while read pack ver
            do
                version["$pack"]="$ver"
                action["$pack"]="**CONFIGURE**"
            done < <( (echo "$line"; cat ) | xargs -d '\n' dpkg-deb --show --showformat='${Package} ${Version}\n')
            ;;
    esac

    for i in "${!version[@]}"
    do
        if [[ "$i" == *"lliurex-meta"* ]]; then
            if [ "${action[$i]}" = "**REMOVE**" ] ; then
                    echo "   [MetaPackage-Protection]: Stopping the uninstall"
                    echo "   [MetaPackage-Protection]: Uninstall blocked because remove metapackage: $i"
                    echo "   [MetaPackage-Protection]: If you want to allow that $i to be uninstalled you must disable protection with dpkg-unlocker-gui or dpkg-unlocker-cli"
                    exit 1
            fi
        fi
    done
fi
exit 0