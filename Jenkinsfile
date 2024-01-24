//Note: the dict keys are literals, not strings
// testing ansible collection

    // Sectigo API is too ****** to have tests
    // certificate: [
    //   moleculeScenarios: [] // ["create"]
    // ],

testAnsibleCollection([
  roleConfigs: [
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
      moleculeScenarios: ["ad","remove", "ldap"]
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
