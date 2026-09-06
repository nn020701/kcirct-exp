// 自动生成：每个低/高电平事件求值后 dump VCD；低电平额外保存 CSV oracle 采样。
#include "Vcsvdut.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

// 按低 32 位 lane 在前的顺序转换任意宽度无符号值，避免 64 位截断。
static std::string decimal(std::vector<uint32_t> words) {
  std::string result;
  do {
    uint64_t carry = 0;
    for (size_t lane = words.size(); lane-- > 0;) {
      const uint64_t value = (carry << 32) | words[lane];
      words[lane] = uint32_t(value / 10);
      carry = value % 10;
    }
    result.push_back(char('0' + carry));
  } while (std::any_of(words.begin(), words.end(), [](uint32_t word) { return word != 0; }));
  std::reverse(result.begin(), result.end());
  return result;
}

int main(int argc, char **argv) {
  VerilatedContext context;
  context.commandArgs(argc, argv);
  context.randReset(0);
  context.traceEverOn(true);
  Vcsvdut dut{&context};
  VerilatedVcdC trace;
  dut.trace(&trace, 1);
  trace.open("trace.vcd");
  std::ifstream stimulus("stimulus.hex");
  std::ofstream output("output.csv");
  if (!stimulus || !output || !trace.isOpen()) return 2;
  output << "M_AXIS_TVALID,M_AXIS_TDATA,M_AXIS_TSTRB,M_AXIS_TLAST\n";

  for (size_t sample = 0; sample < 45; ++sample) {
    dut.M_AXIS_ACLK = 0;
    uint64_t value = 0;
    if (!(stimulus >> std::hex >> value)) return 3; dut.M_AXIS_ARESETN = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.M_AXIS_TREADY = value;
    dut.eval();
    if (context.gotFinish()) return 4;
    trace.dump(context.time());
    output << decimal({uint32_t(uint64_t(dut.M_AXIS_TVALID) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.M_AXIS_TDATA) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.M_AXIS_TSTRB) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.M_AXIS_TLAST) >> 0)}) << "\n";
    if (sample + 1 < 45) {
      context.timeInc(1);
      dut.M_AXIS_ACLK = 1;
      dut.eval();
      if (context.gotFinish()) return 4;
      trace.dump(context.time());
      context.timeInc(1);
    }
  }
  std::string extra;
  if (stimulus >> extra) return 5;
  dut.final();
  trace.close();
  output.close();
  if (!output) return 6;
  return 0;
}
