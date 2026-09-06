PYTHON ?= python3
CASES ?= d13
ARGS ?=
REPORT_ARGS ?=
IR_ARGS ?=
KIMULATOR ?= kcirct

.PHONY: help test inputs prepare prepare-ir run report report-vcd

help:
	@echo "make test                         检查实验脚本和来源契约"
	@echo "make inputs CASES=all-short        将来源 CSV 转为版控的命名输入事件文件"
	@echo "make prepare                      构建 K 定义和专用 parser"
	@echo "make prepare-ir CASES=s2 IR_ARGS='--generation <版本> --activate'  保存常量 initial 转换后的 IR"
	@echo "make run CASES='d13 s3'            通过外部 Kimulator 命令运行双执行 VCD 对照"
	@echo "make run CASES=all-short           运行全部短轨迹变体"
	@echo "make report                       汇总历史 CSV 协议批次"
	@echo "make report-vcd REPORT_ARGS='--runs <批次>'  汇总统一 VCD 协议批次"
	@echo "PYTHON 指定实验解释器；KIMULATOR 指定独立组件命令；ARGS/REPORT_ARGS 传入参数"

test:
	$(PYTHON) -m pytest -q external-defects/tests

inputs:
	$(PYTHON) external-defects/runner.py inputs --cases $(CASES)

prepare:
	$(PYTHON) external-defects/runner.py prepare --kimulator $(KIMULATOR) $(ARGS)

prepare-ir:
	$(PYTHON) external-defects/prepare_ir.py --cases $(CASES) $(IR_ARGS)

run:
	$(PYTHON) external-defects/runner.py run --cases $(CASES) --kimulator $(KIMULATOR) $(ARGS)

report:
	$(PYTHON) external-defects/report.py $(REPORT_ARGS)

report-vcd:
	$(PYTHON) external-defects/report.py --protocol vcd $(REPORT_ARGS)
