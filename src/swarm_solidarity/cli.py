import argparse
import json
from pathlib import Path

from .data import build_messages, expected_answer, generate, write_jsonl


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    gen = commands.add_parser("generate")
    gen.add_argument("--config", default="configs/pilot.json")
    gen.add_argument("--output", default="data/dev/pilot.jsonl")
    example = commands.add_parser("example")
    example.add_argument("--output", default="data/dev/example.json")
    example.add_argument("--config", default="configs/pilot.json")
    args = parser.parse_args()
    if args.command == "generate":
        config = json.loads(Path(args.config).read_text())
        cases = generate(config["dataset_seed"], config["scenario_count"])
        write_jsonl(args.output, cases)
        print(f"Wrote {len(cases)} development cases to {args.output}")
    else:
        config = json.loads(Path(args.config).read_text())
        cases = generate(count=1)
        payload = [{"case": c, "messages": build_messages(c, "original", config.get("context_version", "replay_v1")), "expected_answer": expected_answer(c)} for c in cases]
        Path(args.output).write_text(json.dumps(payload, indent=2) + "\n")
        print(f"Wrote four worked variants to {args.output}")


if __name__ == "__main__":
    main()
