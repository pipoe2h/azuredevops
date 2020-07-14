import os
import json

from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import action, ref, basic_cred, CalmTask
from calm.dsl.builtins import read_local_file, read_ahv_spec, read_vmw_spec, read_file
from calm.dsl.builtins import vm_disk_package
from calm.dsl.builtins import read_env

# import sys
# sys.path.append('blueprint')

from variablestemplate import *

# Import .env variables
ENV = read_env()

AHV_CENTOS_76 = vm_disk_package(
    name="AHV_CENTOS_76",
    config={
        # By default image type is set to DISK_IMAGE
        "image": {
            "source": ENV.get("CENTOS_IMAGE_SOURCE")
        }
    },
)

# Credentials definition
CREDENTIALS = read_env('.local/credentials')

OS_USERNAME = os.getenv("OS_USERNAME") or CREDENTIALS.get("OS_USERNAME")
OS_PASSWORD = os.getenv("OS_PASSWORD") or CREDENTIALS.get("OS_PASSWORD")

Cred_OS = basic_cred(
    username=OS_USERNAME,
    password=OS_PASSWORD,
    name="Cred_OS",
    default=True,
    type="PASSWORD"
)


class CentOS(Service):
    """CentOS for Launching Demo"""


class CentOS_Package(Package):
    """CentOS Package"""

    services = [ref(CentOS)]


class CentOS_Substrate(Substrate):
    """CentOS Substrate"""

    os_type = "Linux"

    provider_spec = read_ahv_spec(
        "centos-spec.yaml",
        disk_packages={1: AHV_CENTOS_76}
    )

    provider_spec.spec["name"] = "jg-azdevops-@@{calm_unique}@@"
    provider_spec.spec["resources"]["nic_list"][0]["subnet_reference"]["name"] = ENV.get("SUBNET_NAME")
    provider_spec.spec["resources"]["nic_list"][0]["subnet_reference"]["uuid"] = ENV.get("SUBNET_UUID")


    readiness_probe = {
        "disabled": False,
        "delay_secs": "60",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(Cred_OS),
    }


class CentOS_Deployment(Deployment):
    """CentOS Deployment"""

    min_replicas = "1"
    max_replicas = "1"

    packages = [ref(CentOS_Package)]
    substrate = ref(CentOS_Substrate)


class Default(Profile):
    """CentOS Profile"""

    ENVIRONMENT = ENVIRONMENT

    deployments = [
        CentOS_Deployment
    ]


class CentOS_Blueprint(Blueprint):
    """CentOS Blueprint"""

    credentials = [
        Cred_OS
    ]
    services = [
        CentOS
    ]
    packages = [
        CentOS_Package,
        AHV_CENTOS_76
    ]
    substrates = [
        CentOS_Substrate
    ]
    profiles = [Default]


def main():
    print(Workload_Mobility_Setup.json_dumps(pprint=True))


if __name__ == "__main__":
    main()