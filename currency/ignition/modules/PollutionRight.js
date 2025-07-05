const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const PollutionRightModule = buildModule("PollutionRightModule", (m) => {
  const deployer = m.getAccount(0);
  const token = m.contract("PollutionRight", [deployer]);

  return { token };
});

module.exports = PollutionRightModule;
