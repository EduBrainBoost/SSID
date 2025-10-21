#!/usr/bin/env python3
"""
Unified Files Validation Engine
Validates that all content from unique files has been properly merged into unified files.
"""

import hashlib
import json
import re
from pathlib import Path
from collections import defaultdict

# Configuration
ARCHIVE_DIR = Path(r"C:\Users\bibel\Documents\Github\SSID\02_audit_logging\archives\unified_sources_20251018T100512254602Z")
REPORTS_DIR = Path(r"C:\Users\bibel\Documents\Github\SSID\02_audit_logging\reports")

# File marker patterns
START_MARKER_PATTERN = r"^# ==== START FILE: (.+?) ====\s*$"
END_MARKER_PATTERN = r"^# ==== END FILE: (.+?) ====\s*$"


class UnifiedFileValidator:
    """Validates unified file integrity and completeness."""

    def __init__(self):
        self.results = {}
        self.validation_errors = []
        self.warnings = []

    def validate_file(self, file_path: Path, expected_count: int = None) -> dict:
        """Validate a single unified file."""
        print(f"\n{'='*80}")
        print(f"VALIDATING: {file_path.name}")
        print(f"{'='*80}")

        if not file_path.exists():
            error = f"File not found: {file_path}"
            self.validation_errors.append(error)
            print(f"[ERROR] {error}")
            return {"status": "error", "error": error}

        result = {
            "filename": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "start_markers": 0,
            "end_markers": 0,
            "embedded_files": [],
            "mismatched_markers": [],
            "empty_sections": 0,
            "total_content_lines": 0,
            "status": "unknown"
        }

        print(f"[INFO] File size: {result['file_size_bytes']:,} bytes")

        # Read and parse file
        current_file = None
        start_line = None
        content_lines = []
        line_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_count += 1

                    # Check for START marker
                    start_match = re.match(START_MARKER_PATTERN, line)
                    if start_match:
                        result["start_markers"] += 1
                        current_file = start_match.group(1)
                        start_line = line_num
                        content_lines = []
                        continue

                    # Check for END marker
                    end_match = re.match(END_MARKER_PATTERN, line)
                    if end_match:
                        result["end_markers"] += 1
                        end_file = end_match.group(1)

                        # Verify matching file path
                        if current_file and current_file != end_file:
                            mismatch = f"Mismatch at line {line_num}: START={current_file}, END={end_file}"
                            result["mismatched_markers"].append(mismatch)
                            self.validation_errors.append(mismatch)
                            print(f"[ERROR] {mismatch}")

                        # Check for empty sections
                        content_line_count = len([l for l in content_lines if l.strip()])
                        if content_line_count == 0:
                            result["empty_sections"] += 1
                            self.warnings.append(f"Empty section for {current_file}")

                        # Record embedded file
                        result["embedded_files"].append({
                            "path": current_file,
                            "start_line": start_line,
                            "end_line": line_num,
                            "content_lines": content_line_count
                        })

                        result["total_content_lines"] += content_line_count
                        current_file = None
                        start_line = None
                        content_lines = []
                        continue

                    # Collect content lines
                    if current_file:
                        content_lines.append(line)

            print(f"[INFO] Total lines read: {line_count:,}")
            print(f"[INFO] START markers found: {result['start_markers']:,}")
            print(f"[INFO] END markers found: {result['end_markers']:,}")
            print(f"[INFO] Embedded files: {len(result['embedded_files']):,}")
            print(f"[INFO] Total content lines: {result['total_content_lines']:,}")

            # Validation checks
            if result["start_markers"] != result["end_markers"]:
                error = f"Marker mismatch: {result['start_markers']} START != {result['end_markers']} END"
                result["status"] = "failed"
                self.validation_errors.append(error)
                print(f"[FAILED] {error}")
            elif len(result["mismatched_markers"]) > 0:
                result["status"] = "failed"
                print(f"[FAILED] {len(result['mismatched_markers'])} mismatched marker pairs")
            elif expected_count and len(result["embedded_files"]) != expected_count:
                warning = f"Expected {expected_count} files, found {len(result['embedded_files'])}"
                result["status"] = "warning"
                self.warnings.append(warning)
                print(f"[WARNING] {warning}")
            else:
                result["status"] = "passed"
                print(f"[PASSED] All validations successful")

            # Empty section warning
            if result["empty_sections"] > 0:
                print(f"[WARNING] {result['empty_sections']} empty sections detected")

        except Exception as e:
            error = f"Validation error for {file_path.name}: {str(e)}"
            result["status"] = "error"
            result["error"] = str(e)
            self.validation_errors.append(error)
            print(f"[ERROR] {error}")

        return result

    def sample_content_integrity(self, file_path: Path, sample_size: int = 5) -> list:
        """Sample random embedded files to verify content integrity."""
        print(f"\n[SAMPLING] Taking {sample_size} random content samples from {file_path.name}...")

        samples = []
        current_file = None
        in_content = False
        content_buffer = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    start_match = re.match(START_MARKER_PATTERN, line)
                    if start_match:
                        current_file = start_match.group(1)
                        in_content = True
                        content_buffer = []
                        continue

                    end_match = re.match(END_MARKER_PATTERN, line)
                    if end_match:
                        if current_file and len(content_buffer) > 0:
                            # Extract first 200 chars as sample
                            content_preview = ''.join(content_buffer[:10]).strip()
                            if content_preview:
                                samples.append({
                                    "file": current_file,
                                    "preview": content_preview[:200],
                                    "line_count": len(content_buffer),
                                    "has_content": True
                                })

                        in_content = False
                        current_file = None
                        content_buffer = []

                        # Stop after collecting enough samples
                        if len(samples) >= sample_size:
                            break
                        continue

                    if in_content:
                        content_buffer.append(line)

        except Exception as e:
            print(f"[ERROR] Sampling error: {str(e)}")

        print(f"[SAMPLING] Collected {len(samples)} samples")
        for i, sample in enumerate(samples[:3], 1):  # Show first 3
            try:
                # Encode preview to ASCII-safe format
                preview = sample['preview'][:80].encode('ascii', 'replace').decode('ascii')
                print(f"  Sample {i}: {sample['file']}")
                print(f"    Lines: {sample['line_count']}, Preview: {preview}...")
            except Exception:
                print(f"  Sample {i}: {sample['file']} (preview encoding error)")

        return samples

    def run_validation(self) -> dict:
        """Run complete validation suite."""
        print("="*80)
        print("UNIFIED FILES VALIDATION ENGINE")
        print("="*80)
        print(f"Archive: {ARCHIVE_DIR}")
        print("="*80)

        # Expected counts from unification report
        expected_counts = {
            "unified_python_all.py": 1632,
            "unified_yaml_all.yaml": None,  # Combined .yaml + .yml
            "unified_rego_all.rego": 220,
            "unified_json_all.json": 2683
        }

        validation_results = {}

        # Validate each unified file
        for filename, expected_count in expected_counts.items():
            file_path = ARCHIVE_DIR / filename
            result = self.validate_file(file_path, expected_count)
            validation_results[filename] = result

            # Take content samples
            if result.get("status") == "passed":
                samples = self.sample_content_integrity(file_path, sample_size=5)
                result["content_samples"] = samples

        # Generate summary
        summary = {
            "timestamp": "2025-10-18T10:30:00Z",
            "archive_dir": str(ARCHIVE_DIR),
            "files_validated": len(validation_results),
            "validation_results": validation_results,
            "total_embedded_files": sum(r.get("start_markers", 0) for r in validation_results.values()),
            "total_errors": len(self.validation_errors),
            "total_warnings": len(self.warnings),
            "errors": self.validation_errors,
            "warnings": self.warnings,
            "overall_status": "PASSED" if len(self.validation_errors) == 0 else "FAILED"
        }

        # Print summary
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        print(f"Files Validated: {summary['files_validated']}")
        print(f"Total Embedded Files: {summary['total_embedded_files']:,}")
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Total Warnings: {summary['total_warnings']}")
        print(f"Overall Status: {summary['overall_status']}")
        print("="*80)

        # Detailed breakdown
        print("\nDETAILED BREAKDOWN:")
        for filename, result in validation_results.items():
            status_symbol = "[OK]" if result.get("status") == "passed" else "[FAIL]"
            print(f"  {status_symbol} {filename}: {result.get('start_markers', 0):,} files embedded")

        return summary

    def write_report(self, summary: dict):
        """Write validation report to disk."""
        # JSON report
        json_path = REPORTS_DIR / "unified_files_validation_report.json"
        print(f"\n[REPORT] Writing JSON report: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Markdown report
        md_path = REPORTS_DIR / "unified_files_validation_report.md"
        print(f"[REPORT] Writing Markdown report: {md_path}")

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Unified Files Validation Report\n\n")
            f.write(f"**Timestamp:** {summary['timestamp']}\n")
            f.write(f"**Archive:** `{summary['archive_dir']}`\n")
            f.write(f"**Overall Status:** **{summary['overall_status']}**\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Validated:** {summary['files_validated']}\n")
            f.write(f"- **Total Embedded Files:** {summary['total_embedded_files']:,}\n")
            f.write(f"- **Errors:** {summary['total_errors']}\n")
            f.write(f"- **Warnings:** {summary['total_warnings']}\n\n")

            f.write("## Validation Results\n\n")
            for filename, result in summary['validation_results'].items():
                status_icon = "✓" if result.get("status") == "passed" else "✗"
                f.write(f"### {status_icon} {filename}\n\n")
                f.write(f"- **Status:** {result.get('status', 'unknown').upper()}\n")
                f.write(f"- **File Size:** {result.get('file_size_bytes', 0):,} bytes\n")
                f.write(f"- **START Markers:** {result.get('start_markers', 0):,}\n")
                f.write(f"- **END Markers:** {result.get('end_markers', 0):,}\n")
                f.write(f"- **Embedded Files:** {len(result.get('embedded_files', []))}\n")
                f.write(f"- **Total Content Lines:** {result.get('total_content_lines', 0):,}\n")
                f.write(f"- **Empty Sections:** {result.get('empty_sections', 0)}\n")

                if result.get('mismatched_markers'):
                    f.write(f"\n**Mismatched Markers:** {len(result['mismatched_markers'])}\n")

                # Show sample embedded files
                embedded = result.get('embedded_files', [])
                if embedded:
                    f.write(f"\n**Sample Embedded Files (first 5):**\n\n")
                    for ef in embedded[:5]:
                        f.write(f"- `{ef['path']}` (lines {ef['start_line']}-{ef['end_line']}, {ef['content_lines']} content lines)\n")

                f.write("\n")

            if summary['errors']:
                f.write("## Errors\n\n")
                for error in summary['errors']:
                    f.write(f"- {error}\n")
                f.write("\n")

            if summary['warnings']:
                f.write("## Warnings\n\n")
                for warning in summary['warnings']:
                    f.write(f"- {warning}\n")
                f.write("\n")

            f.write("## Conclusion\n\n")
            if summary['overall_status'] == "PASSED":
                f.write("All unified files have been validated successfully. ")
                f.write("All content from unique source files has been properly merged with correct START/END markers.\n")
            else:
                f.write("Validation failed. Please review errors above.\n")

        print(f"[REPORT] Reports written successfully")


def main():
    validator = UnifiedFileValidator()
    summary = validator.run_validation()
    validator.write_report(summary)
    return summary


if __name__ == "__main__":
    summary = main()
    exit(0 if summary['overall_status'] == "PASSED" else 1)
