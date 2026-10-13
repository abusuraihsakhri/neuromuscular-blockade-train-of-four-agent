"""Command-line interface for legacy demonstrations and educational TOF interpretation."""
import argparse
import csv
import json
import sys
from pathlib import Path
from .models import ClinicalCasePayload
from .agents import TOFCoordinator
from .tof import interpret_tof

coordinator = TOFCoordinator()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="neuromuscular-blockade-train-of-four-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_tof = subparsers.add_parser("tof", help="Interpret measured TOF observations (educational only)")
    p_tof.add_argument("--count", type=int, required=True, help="Detected TOF twitches, 0–4")
    p_tof.add_argument("--ptc", type=int, help="Post-tetanic count, only when TOF count is 0")
    p_tof.add_argument("--ratio", type=float, help="Quantitative TOF ratio, only when count is 4")
    p_audit = subparsers.add_parser("audit", help="Legacy generic-metric demonstration (not clinical)")
    p_audit.add_argument("--case-id", default="CASE-2026-001")
    p_audit.add_argument("--primary", type=float, default=26.2)
    p_audit.add_argument("--secondary", type=float, default=12.5)
    p_audit.add_argument("--stat", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")
    p_chat = subparsers.add_parser("chat", help="Legacy system information")
    p_chat.add_argument("query", nargs="+")
    p_batch = subparsers.add_parser("batch", help="Legacy CSV audit demonstration")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")
    p_serve = subparsers.add_parser("serve", help="Launch optional FastAPI service")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    if args.command == "tof":
        try:
            print(json.dumps(interpret_tof(args.count, args.ptc, args.ratio), indent=2))
        except ValueError as exc:
            print(f"Invalid TOF observations: {exc}", file=sys.stderr)
            return 2
        return 0

    if args.command == "audit":
        print("DEMONSTRATION ONLY: generic metrics are not validated TOF measurements.", file=sys.stderr)
        case = ClinicalCasePayload(
            case_id=args.case_id, patient_synthetic_id="SYNTH-PT-881",
            primary_metric=args.primary, secondary_metric=args.secondary,
            status_flag=args.status, is_stat=args.stat,
        )
        print(json.dumps(coordinator.process_case(case), indent=2))
        return 0

    if args.command == "chat":
        print(coordinator.query_supervisory_chat(" ".join(args.query)))
        return 0

    if args.command == "batch":
        input_path = Path(args.input)
        try:
            if not input_path.is_file():
                raise ValueError("Input CSV file not found.")
            if input_path.stat().st_size > 100 * 1024 * 1024:
                raise ValueError("Input CSV file exceeds 100 MiB limit.")
            with input_path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    raise ValueError("CSV must have a header row.")
                fields = list(reader.fieldnames)
                records = list(reader)
            additions = ["overall_status", "total_alerts", "stat_critical_alerts", "consensus_summary"]
            output_rows = []
            for line_number, row in enumerate(records, 2):
                try:
                    case = ClinicalCasePayload(
                        case_id=row.get("case_id") or "CASE-01",
                        patient_synthetic_id=row.get("patient_synthetic_id") or "SYNTH-01",
                        primary_metric=float(row.get("metric_primary") or row.get("primary_metric") or 15),
                        secondary_metric=float(row.get("metric_secondary") or row.get("secondary_metric") or 5),
                        status_flag=row.get("status_flag") or row.get("status_text") or "NORMAL",
                        is_stat=str(row.get("is_stat") or row.get("critical_flag") or "").strip().lower() in ("true", "1", "yes"),
                    )
                except (ValueError, TypeError) as exc:
                    print(f"Skipping malformed CSV row {line_number}: {exc}", file=sys.stderr)
                    continue
                dossier = coordinator.process_case(case)
                output_rows.append({**row, **{k: dossier[k] for k in additions}})
            with Path(args.output).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(dict.fromkeys(fields + additions)), extrasaction="ignore")
                writer.writeheader()
                writer.writerows(output_rows)
        except (OSError, ValueError, UnicodeError, csv.Error) as exc:
            print(f"CSV operation failed: {exc}", file=sys.stderr)
            return 1
        print(f"Batch processed {len(output_rows)} rows -> {args.output}")
        return 0

    if args.command == "serve":
        try:
            import uvicorn
            from .server import create_app
            app = create_app()
            if app is None:
                raise ImportError("FastAPI unavailable")
        except ImportError:
            print("Install optional API dependencies: pip install -e '.[api]'", file=sys.stderr)
            return 1
        uvicorn.run(app, host=args.host, port=args.port)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
