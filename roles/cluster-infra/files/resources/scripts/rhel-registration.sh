#!/bin/bash -eu

set -o pipefail

OS_ID="$(source /etc/os-release; echo $ID)"
if [[ "$OS_ID" != "rhel" ]] && [[ "$OS_ID" != "centos" ]]; then
    echo "WARNING: Subscription is only supported for RHEL and CENTOS Images. This is a $OS_ID Image"
    exit 1
fi


REG_FORCE=$RHEL_REG_FORCE
REG_ORG=$RHEL_REG_ORG
REG_ACTIVATION_KEY=$RHEL_REG_ACTIVATION_KEY
REG_SAT_URL=$RHEL_REG_SAT_URL
ZONE=$ZONE

retry_max_count=10
opts=



if [ -n "${REG_FORCE:-}" ]; then
    opts="$opts --force"
fi

if [ -n "${REG_ACTIVATION_KEY:-}" ]; then
    opts="$opts --activationkey=$REG_ACTIVATION_KEY"

    if [ -z "${REG_ORG:-}" ]; then
        echo "WARNING: REG_ACTIVATION_KEY set without REG_ORG."
    fi
fi

if [ -n "${REG_ORG:-}" ]; then
    opts="$opts --org=$REG_ORG"
fi


function retry() {
    # Inhibit -e since we want to retry without exiting..
    set +e
    # Retry delay (seconds)
    retry_delay=2.0
    retry_count=0
    mycli="$@"
    while [ $retry_count -lt ${retry_max_count} ]
    do
        echo "INFO: Sleeping ${retry_delay} ..."
        sleep ${retry_delay}
        echo "INFO: Executing '${mycli}' ..."
        ${mycli}
        if [ $? -eq 0 ]; then
            echo "INFO: Ran '${mycli}' successfully, not retrying..."
            break
        else
            echo "WARN: Failed to connect when running '${mycli}', retrying (attempt #$retry_count )..."
            retry_count=$(echo $retry_count + 1 | bc)
        fi
    done

    if [ $retry_count -ge ${retry_max_count} ]; then
        echo "ERROR: Failed to connect after ${retry_max_count} attempts when running '${mycli}'"
        exit 1
    fi
    # Re-enable -e when exiting retry()
    set -e
}

if [ "$OS_ID" == "centos" ]; then
  sudo yum install -y subscription-manager # centos does not have the subscription-manager pre-installed
fi

# we might get a zone passed with a dot at the end, so remove it before
if [ -n "${ZONE:-}" ]; then
    DOMAIN=$(echo $ZONE | sed -e 's/\.$//g')
    echo "Setting fully qualified hostname to $DOMAIN"
    hostname=$(hostname)
    hostnamectl set-hostname "$hostname".$DOMAIN
fi

rpm -Uvh "$REG_SAT_URL/pub/katello-ca-consumer-latest.noarch.rpm"
retry subscription-manager register $opts
yum install -y katello-agent || true # needed for errata reporting to satellite6
katello-package-upload
