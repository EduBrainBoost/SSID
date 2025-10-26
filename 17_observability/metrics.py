
import json, time, os
def emit(metric_name, value, labels=None):
    labels = labels or {}
    line = json.dumps({"t": time.time(), "metric": metric_name, "value": value, "labels": labels})
    print(line)


def emit_counter(name, inc=1, labels=None):
    labels = labels or {}
    emit(name, inc, labels)

def emit_histogram(name, value, labels=None):
    labels = labels or {}
    emit(name, value, labels)

def track_boot_latency(seconds, root="ALL"):
    emit_histogram("maos.boot.seconds", seconds, {"root": root})

def track_warnings(count, root="ALL"):
    emit_counter("maos.warn.count", count, {"root": root})

def track_drift(count):
    emit_counter("maos.drift.count", count, {})
