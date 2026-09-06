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
  output << "s_axis_tready,m_axis_tdata,m_axis_tkeep,m_axis_tvalid,m_axis_tlast,m_axis_tid,m_axis_tdest,m_axis_tuser\n";

  for (size_t sample = 0; sample < 14; ++sample) {
    dut.clk = 0;
    uint64_t value = 0;
    if (!(stimulus >> std::hex >> value)) return 3; dut.rst = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tdata = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tkeep = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tvalid = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tlast = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tid = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tdest = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.s_axis_tuser = value;
    if (!(stimulus >> std::hex >> value)) return 3; dut.m_axis_tready = value;
    dut.eval();
    if (context.gotFinish()) return 4;
    trace.dump(context.time());
    output << decimal({uint32_t(uint64_t(dut.s_axis_tready) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tdata) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tkeep) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tvalid) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tlast) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tid) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tdest) >> 0)}) << ",";
    output << decimal({uint32_t(uint64_t(dut.m_axis_tuser) >> 0)}) << "\n";
    if (sample + 1 < 14) {
      context.timeInc(1);
      dut.clk = 1;
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
