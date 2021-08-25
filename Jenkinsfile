//Note: the dict keys are literals, not strings
// testing ansible collection
testAnsibleCollection([
  roleConfigs: [
    beegfs_client: [
      moleculeScenarios: [] // fails due to kernel requirements
    ],
    dns: [
      moleculeScenarios: ["default"]
    ],
    cuda: [
      moleculeScenarios: [] // fails due to kernel requirements
    ],
    slurm: [
      moleculeScenarios: ["centos7", "stream8"]
    ],
  ]
])