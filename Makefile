PYTHON ?= python3
CASES ?= d13
ARGS ?=
REPORT_ARGS ?=

.PHONY: help test prepare run report

help:
	@echo "make test                         检查实验脚本和来源契约"
	@echo "make prepare                      构建 K 定义和专用 parser"
	@echo "make run CASES='d13 s3'            运行指定缺陷变体"
	@echo "make run CASES=all-short           运行全部短轨迹变体"
	@echo "make report                       汇总已保存的批次结果"
	@echo "PYTHON 指定解释器；ARGS 传入 runner 参数，REPORT_ARGS 传入报告参数"

test:
	$(PYTHON) -m pytest -q external-defects/tests

prepare:
	$(PYTHON) external-defects/runner.py prepare $(ARGS)

run:
	$(PYTHON) external-defects/runner.py run --cases $(CASES) $(ARGS)

report:
	$(PYTHON) external-defects/report.py $(REPORT_ARGS)
