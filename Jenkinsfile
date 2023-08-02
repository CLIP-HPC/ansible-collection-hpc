@Library('vbc-cicd@RFC-2547-upgrade-to-ee-environment') _

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
      moleculeScenarios: ["default","remove"]
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
