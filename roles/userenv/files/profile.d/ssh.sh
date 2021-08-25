
if [ "$(id -u 2>/dev/null)" != "0" ]; then
  if [ ! -f ~/.ssh/id_ecdsa ]; then
    if [ -w ~ ]; then
      echo Creating ECDSA key for ssh
      ssh-keygen -t ecdsa -f ~/.ssh/id_ecdsa -q -N ""
      cat ~/.ssh/id_ecdsa.pub >> ~/.ssh/authorized_keys
      chmod 600 ~/.ssh/authorized_keys ~/.ssh/id_ecdsa ~/.ssh/id_ecdsa.pub
    fi
  fi
fi

