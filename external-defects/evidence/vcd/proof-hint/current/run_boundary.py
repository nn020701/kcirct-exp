"""从原始 S2 prestate 连续执行，核对插桩版本边界并保存 proof hint。"""
from pathlib import Path
import hashlib
import json
import os
import re
import signal
import subprocess
import time

from pyk.kore.parser import KoreParser

WORK = Path(__file__).resolve().parent
EXP = WORK.parents[3]
SOURCE = EXP / "evidence/vcd/metadata-integrity/vcd-complete-02/diagnosis/replay-0.kore.prestate"
DEFINITION = WORK / "definition"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(node):
    yield node
    for child in node.patterns:
        yield from walk(child)


def inspect(path):
    tree = KoreParser(path.read_text()).pattern()
    connection = next(n for n in walk(tree) if getattr(n, "symbol", "") == "Lbl'-LT-'connection'-GT-'")
    item = next(n for n in walk(connection)
                if getattr(n, "symbol", "") == "Lbl'UndsPipe'-'-GT-Unds'"
                and n.args[0].text == 'inj{SortString{}, SortKItem{}}(\\dv{SortString{}}("xlnxstream_2018_3/%53"))')
    result = {"connection_sha256": hashlib.sha256(connection.text.encode()).hexdigest(),
              "mux_and_args": re.findall(r'\\dv\{SortString\{\}\}\("([^"]*)"\)', item.args[1].text)[:4]}
    for n in walk(tree):
        if getattr(n, "symbol", "") == "Lbl'-LT-'current-info'-GT-'":
            cells = {c.symbol: c for c in n.args}
            if '"14214"' in cells["Lbl'-LT-'current-id'-GT-'"].text:
                result["current_14214"] = cells["Lbl'-LT-'current'-GT-'"].text
    return result


def main():
    assert json.loads((WORK / "build.json").read_text())["returncode"] == 0
    assert sha(SOURCE) == "2a291c7f2c7d20330c2128a95eeae0ad3ccf7d3fc8d371fe8bd46f54d585bdc1"
    env = os.environ.copy()
    env.pop("K_BIN", None)
    env["PATH"] = str(Path.home() / ".nix-profile/bin") + os.pathsep + env["PATH"]
    baseline = inspect(SOURCE)
    records = []
    for depth, hint in ((1023, False), (1024, False), (1024, True)):
        name = f"depth-{depth}" + (".hint" if hint else ".kore")
        output = WORK / name
        assert not output.exists(), output
        argv = [str(Path.home() / ".nix-profile/bin/krun"), str(SOURCE),
                "--definition", str(DEFINITION), "--parser", "cat", "--term",
                "--no-expand-macros", "--depth", str(depth)]
        argv += ["--proof-hint"] if hint else ["--output", "kore"]
        record = {"argv": argv, "cwd": str(WORK), "source_sha256": sha(SOURCE),
                  "definition_sha256": sha(DEFINITION / "definition.kore"),
                  "output": name, "started_at": time.time(), "proof_hint": hint}
        records.append(record)
        (WORK / "runs.json").write_text(json.dumps(records, indent=2) + "\n")
        with output.open("wb") as out, (WORK / (name + ".stderr")).open("wb") as err:
            proc = subprocess.Popen(argv, env=env, cwd=WORK, stdout=out, stderr=err, start_new_session=True)
            try:
                rc = proc.wait(timeout=180)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=10)
                rc = 124
        record.update(returncode=rc, elapsed_seconds=time.time() - record["started_at"],
                      output_bytes=output.stat().st_size, output_sha256=sha(output))
        if rc == 0 and not hint:
            record["state"] = inspect(output)
            record["connection_unchanged"] = record["state"]["connection_sha256"] == baseline["connection_sha256"]
            old = EXP / f"evidence/vcd/metadata-integrity/vcd-complete-02/diagnosis/depth-{depth}.kore"
            record["matches_original_boundary_bytes"] = output.read_bytes() == old.read_bytes()
        (WORK / "runs.json").write_text(json.dumps(records, indent=2) + "\n")
        print(name, rc, record.get("connection_unchanged"), output.stat().st_size, flush=True)
        assert rc == 0


if __name__ == "__main__":
    main()
