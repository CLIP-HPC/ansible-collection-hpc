@Library('vbc-cicd@ansible_collections') _

//Note: the dict keys are literals, not strings
// testing ansible collection
testAnsibleCollection([
  roleConfigs: [
    certificate: [
      moleculeScenarios: ["create"]
    ],
    container: [
      moleculeScenarios: ["certificates", "files", "systemd","systemd_caps","ulimits","update_image"]
    ],
    dns: [
      moleculeScenarios: ["default"]
    ],
    firewalld: [
      moleculeScenarios: ["default"]
    ],
    ntp: [
      moleculeScenarios: ["default"]
    ],
    promtail: [
      moleculeScenarios: ["default"]
    ],
    sssd: [
      moleculeScenarios: ["default-centos7","default-centos8","default-ubi","remove-centos7", "remove-centos8","remove-ubi"]
    ],
    sudoers: [
      moleculeScenarios: ["default", "remove"]
    ],
    syslog: [
      moleculeScenarios: ["default"]
    ],
    user: [
      moleculeScenarios: ["default"]
    ]
  ]
])