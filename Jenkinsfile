//Note: the dict keys are literals, not strings
// testing ansible collection
testAnsibleCollection([
  roleConfigs: [
    // Sectigo API is too ****** to have tests 
    // certificate: [
    //   moleculeScenarios: [] // ["create"]
    // ],
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
      moleculeScenarios: ["default-centos7","default-ubi","remove-centos7","remove-ubi"]
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
