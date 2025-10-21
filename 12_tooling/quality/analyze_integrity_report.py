#!/usr/bin/env python3
import json
import sys

if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

with open('02_audit_logging/reports/fake_integrity_analysis_report.json', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("FAKE-INTEGRITY ANALYSIS - DETAILED BREAKDOWN")
print("=" * 80)
print()

print(f"Total Anomalies: {data['summary']['total_anomalies']}")
print(f"  High Severity: {data['summary']['high_severity_count']}")
print(f"  Medium Severity: {data['summary']['medium_severity_count']}")
print(f"  Low Severity: {data['summary']['low_severity_count']}")
print()

print("Categories:")
print(f"  Root breaks: {len(data['categories']['root_breaks'])}")
print(f"  Score manipulation: {len(data['categories']['score_manipulation'])}")
print(f"  Evidence loops: {len(data['categories']['evidence_loops'])}")
print(f"  Policy shields: {len(data['categories']['policy_shields'])}")
print(f"  Hash duplicates: {len(data['categories']['hash_duplicates'])}")
print()

print("=" * 80)
print("HASH DUPLICATES ANALYSIS")
print("=" * 80)
dupes = data['categories']['hash_duplicates']
print(f"Total: {len(dupes)}")
print()

# Group by file count
by_count = {}
for d in dupes:
    count = d['count']
    by_count[count] = by_count.get(count, 0) + 1

print("Distribution by duplicate count:")
for count in sorted(by_count.keys(), reverse=True)[:10]:
    print(f"  {count} duplicates: {by_count[count]} hash groups")
print()

print("Top 10 most duplicated hashes:")
sorted_dupes = sorted(dupes, key=lambda x: x['count'], reverse=True)
for i, d in enumerate(sorted_dupes[:10], 1):
    print(f"{i}. Hash {d['hash']}: {d['count']} files")
    for f in d['files'][:5]:
        print(f"     - {f}")
    if len(d['files']) > 5:
        print(f"     ... and {len(d['files']) - 5} more")
    print()

print("=" * 80)
print("SCORE MANIPULATION PATTERNS")
print("=" * 80)
score_manip = data['categories']['score_manipulation']
print(f"Total: {len(score_manip)}")
print()
print("Files flagged (first 10):")
for s in score_manip[:10]:
    print(f"  - {s['path']}")
    print(f"    Type: {s['type']}, Has validation: {s.get('has_validation', 'N/A')}")
print()

print("=" * 80)
print("POLICY SHIELD ISSUES")
print("=" * 80)
policies = data['categories']['policy_shields']
print(f"Total: {len(policies)}")
for p in policies:
    print(f"  - {p['type']}: {p.get('path', 'N/A')}")
    print(f"    Severity: {p.get('severity')}, Note: {p.get('note', 'N/A')}")
print()

print("=" * 80)
print("INTERPRETATION")
print("=" * 80)
interp = data['interpretation']
print(f"Risk: {interp['risk']}")
print(f"Message: {interp['message']}")
print()
print("Recommendations:")
for r in interp['recommendations']:
    print(f"  - {r}")
