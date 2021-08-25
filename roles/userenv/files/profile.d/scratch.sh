SCRATCHFS='/scratch-cbe'
# check if mount point exists, if not bail without error
if [ ! -d "${SCRATCHFS}" ]; then
  return
fi
#check if the FS is not hanging, bail if it is.
read -t 3 < <(stat -t "${SCRATCHFS}")
if [ $? -eq 1 ]; then
   echo 'BeegFS /scratch-cbe hanging or otherwise not available. Skipping creation of user folder'
   return
fi

SCRATCHDIR="${SCRATCHFS}/users/${USER}"
if [ "$(id -u 2>/dev/null)" != "0" ]; then
    if [ ! -d "${SCRATCHDIR}" ]; then
        mkdir -p "${SCRATCHDIR}";
        chmod 1777 "${SCRATCHDIR}";
    fi
fi

export SCRATCHDIR
