#!/usr/bin/env python3
"""
Progress Tracker: Real-time Compliance Score and Phase Progress Monitor
=============================================================================
Trackt den Fortschritt durch alle 5 Phasen der Root24-Implementation:
- Berechnet Compliance-Score basierend auf implementierten Requirements
- Monitort Phase-Status und KPI-Targets
- Generiert Fortschrittsberichte für Dashboard
- Warnt bei Abweichungen vom Plan

Exit Codes:
  0 = Success
  1 = Progress behind target
  2 = Critical KPI missed
  3 = Configuration error
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

# --- KONFIGURATION ---
REPO_ROOT = Path(__file__).parent.parent.parent
TIMELINE_MATRIX = REPO_ROOT / "23_compliance" / "roadmap" / "timeline_matrix.yaml"
DASHBOARD_CONFIG = REPO_ROOT / "23_compliance" / "roadmap" / "phase_dashboard.json"
PROGRESS_STATE_FILE = REPO_ROOT / "02_audit_logging" / "progress_state.json"
LOG_FILE = REPO_ROOT / "02_audit_logging" / "progress_tracker.log"

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- DATENSTRUKTUREN ---

class PhaseStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    AT_RISK = "at_risk"

class DeliverableStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class KPI:
    """Key Performance Indicator"""
    id: str
    name: str
    type: str
    target: Optional[float]
    current: Optional[float]
    unit: str
    critical: bool = False
    met: bool = False

    def calculate_percentage(self) -> Optional[float]:
        """Berechnet Zielerreichung in %"""
        if self.target is None or self.current is None:
            raise NotImplementedError("TODO: Implement this function")
        if self.target == 0:
            return 100.0 if self.current == 0 else 0.0
        return (self.current / self.target) * 100.0

@dataclass
class Deliverable:
    """Phase Deliverable"""
    id: str
    name: str
    status: DeliverableStatus
    progress: float
    owner: str
    requirements: List[str] = field(default_factory=list)

@dataclass
class Phase:
    """Implementation Phase"""
    id: str
    name: str
    number: int
    status: PhaseStatus
    week_start: int
    week_end: int
    score_baseline: int
    score_target: int
    kpis: List[KPI] = field(default_factory=list)
    deliverables: List[Deliverable] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None

    def calculate_progress(self) -> float:
        """Berechnet Gesamt-Fortschritt der Phase (0-100%)"""
        if not self.deliverables:
            return 0.0
        total_progress = sum(d.progress for d in self.deliverables)
        return total_progress / len(self.deliverables)

    def is_on_track(self, current_week: int) -> bool:
        """Prüft, ob Phase im Zeitplan ist"""
        if self.status == PhaseStatus.COMPLETED:
            return True
        if current_week > self.week_end and self.status != PhaseStatus.COMPLETED:
            return False
        return True

    def calculate_score_progress(self) -> float:
        """Berechnet Score-Fortschritt (0-100%)"""
        total_increment = self.score_target - self.score_baseline
        if total_increment == 0:
            return 100.0
        # Basierend auf Deliverable-Progress
        phase_progress = self.calculate_progress()
        return phase_progress

@dataclass
class ProgressState:
    """Aktueller Gesamt-Fortschritt"""
    current_score: float
    target_score: float
    current_week: int
    current_phase: int
    phases: List[Phase]
    last_updated: datetime
    start_date: datetime
    estimated_completion: datetime

    def calculate_overall_progress(self) -> float:
        """Berechnet Gesamt-Fortschritt (0-100%)"""
        completed_phases = sum(1 for p in self.phases if p.status == PhaseStatus.COMPLETED)
        total_phases = len(self.phases)

        # Anteil von vollständigen Phasen
        base_progress = (completed_phases / total_phases) * 100

        # Plus Fortschritt der aktuellen Phase
        if self.current_phase <= len(self.phases):
            current = self.phases[self.current_phase - 1]
            phase_weight = 100 / total_phases
            base_progress += (current.calculate_progress() / 100) * phase_weight

        return min(base_progress, 100.0)

    def is_behind_schedule(self) -> bool:
        """Prüft, ob hinter dem Zeitplan"""
        expected_week = self._calculate_expected_week()
        return self.current_week > expected_week

    def _calculate_expected_week(self) -> int:
        """Berechnet erwartete Woche basierend auf aktuellem Datum"""
        if not hasattr(self, 'start_date') or self.start_date is None:
            return 1
        delta = datetime.now() - self.start_date
        return int(delta.days / 7) + 1

    def is_score_on_track(self) -> bool:
        """Prüft, ob Score im Ziel ist"""
        # Expected score basierend auf Phasen
        expected_score = self._calculate_expected_score()
        # Toleranz: -5 Punkte
        return self.current_score >= (expected_score - 5)

    def _calculate_expected_score(self) -> float:
        """Berechnet erwarteten Score basierend auf aktueller Woche"""
        for phase in self.phases:
            if phase.week_start <= self.current_week <= phase.week_end:
                # Linear interpolation innerhalb Phase
                week_progress = (self.current_week - phase.week_start) / (phase.week_end - phase.week_start + 1)
                score_increment = phase.score_target - phase.score_baseline
                return phase.score_baseline + (week_progress * score_increment)

        # Fallback: Baseline oder Target
        if self.current_week < self.phases[0].week_start:
            return self.phases[0].score_baseline
        return self.phases[-1].score_target

# --- DATEN-LADEN ---

def load_timeline_matrix() -> Dict:
    """Lädt Timeline-Matrix YAML"""
    if not TIMELINE_MATRIX.exists():
        raise FileNotFoundError(f"Timeline matrix not found: {TIMELINE_MATRIX}")

    with open(TIMELINE_MATRIX, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_dashboard_config() -> Dict:
    """Lädt Dashboard-Config JSON"""
    if not DASHBOARD_CONFIG.exists():
        raise FileNotFoundError(f"Dashboard config not found: {DASHBOARD_CONFIG}")

    with open(DASHBOARD_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_progress_state() -> Optional[Dict]:
    """Lädt persistierten Progress-State"""
    if not PROGRESS_STATE_FILE.exists():
        raise NotImplementedError("TODO: Implement this function")

    with open(PROGRESS_STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_progress_state(state: ProgressState):
    """Speichert Progress-State"""
    state_dict = asdict(state)

    # Konvertiere datetime zu ISO-String
    if isinstance(state_dict.get('last_updated'), datetime):
        state_dict['last_updated'] = state_dict['last_updated'].isoformat()
    if isinstance(state_dict.get('start_date'), datetime):
        state_dict['start_date'] = state_dict['start_date'].isoformat()
    if isinstance(state_dict.get('estimated_completion'), datetime):
        state_dict['estimated_completion'] = state_dict['estimated_completion'].isoformat()

    # Konvertiere Enums zu Strings
    for phase in state_dict.get('phases', []):
        if 'status' in phase and hasattr(phase['status'], 'value'):
            phase['status'] = phase['status'].value
        for deliv in phase.get('deliverables', []):
            if 'status' in deliv and hasattr(deliv['status'], 'value'):
                deliv['status'] = deliv['status'].value

    with open(PROGRESS_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state_dict, f, indent=2, default=str)

    logger.info(f"Progress state saved to {PROGRESS_STATE_FILE}")

# --- INITIALISIERUNG ---

def initialize_progress_state(timeline: Dict, dashboard: Dict) -> ProgressState:
    """Initialisiert Progress-State aus Timeline und Dashboard"""

    # Parse Start-Date
    start_date_str = timeline.get('metadata', {}).get('start_date', '2025-01-07')
    start_date = datetime.fromisoformat(start_date_str)

    # Parse Estimated Completion
    completion_str = timeline.get('metadata', {}).get('estimated_completion', '2025-03-18')
    estimated_completion = datetime.fromisoformat(completion_str)

    # Berechne aktuelle Woche
    current_week = max(1, int((datetime.now() - start_date).days / 7) + 1)

    # Parse Phasen
    phases = []
    for phase_key in ['phase_1_inventar', 'phase_2_must', 'phase_3_should', 'phase_4_may', 'phase_5_tests_evidence']:
        phase_data = timeline.get(phase_key, {})
        phase_dashboard = dashboard['phases'].get(phase_key.replace('_inventar', '').replace('_must', '').replace('_should', '').replace('_may', '').replace('_tests_evidence', ''), {})

        phase_num = phase_data.get('phase_number', 1)
        timeline_data = phase_data.get('timeline', {})
        scores_data = phase_data.get('scores', {})

        # KPIs
        kpis = []
        for kpi_data in phase_dashboard.get('kpis', []):
            kpis.append(KPI(
                id=kpi_data['id'],
                name=kpi_data['name'],
                type=kpi_data['type'],
                target=kpi_data.get('target'),
                current=kpi_data.get('current', 0),
                unit=kpi_data['unit'],
                critical=kpi_data.get('critical', False)
            ))

        # Deliverables
        deliverables = []
        for deliv_data in phase_data.get('deliverables', []):
            deliverables.append(Deliverable(
                id=deliv_data['id'],
                name=deliv_data['name'],
                status=DeliverableStatus.PENDING,
                progress=0.0,
                owner=deliv_data['owner'],
                requirements=deliv_data.get('requirements', [])
            ))

        phase = Phase(
            id=phase_key,
            name=phase_data.get('name', ''),
            number=phase_num,
            status=PhaseStatus.NOT_STARTED if phase_num > 1 else PhaseStatus.IN_PROGRESS,
            week_start=timeline_data.get('start_week', 1),
            week_end=timeline_data.get('end_week', 1),
            score_baseline=scores_data.get('baseline', 0),
            score_target=scores_data.get('target', 0),
            kpis=kpis,
            deliverables=deliverables
        )
        phases.append(phase)

    return ProgressState(
        current_score=timeline.get('metadata', {}).get('baseline_score', 20),
        target_score=timeline.get('metadata', {}).get('target_score', 100),
        current_week=current_week,
        current_phase=1,
        phases=phases,
        last_updated=datetime.now(),
        start_date=start_date,
        estimated_completion=estimated_completion
    )

# --- FORTSCHRITTS-BERECHNUNG ---

def update_progress_from_sources(state: ProgressState) -> ProgressState:
    """Updated Progress-State aus externen Datenquellen (Logic-Gap-Tester, etc.)"""

    raise NotImplementedError("TODO: Implement this block")
    # logic_gaps = run_logic_gap_tester()
    # state.current_score = calculate_score_from_gaps(logic_gaps)

    raise NotImplementedError("TODO: Implement this block")
    # coverage = run_coverage_tool()
    # update_test_kpis(state, coverage)

    # Für jetzt: Schätze Score basierend auf Phase-Fortschritt
    state.current_score = estimate_score_from_phases(state)

    state.last_updated = datetime.now()
    return state

def estimate_score_from_phases(state: ProgressState) -> float:
    """Schätzt Score basierend auf Phase-Fortschritt"""
    total_score = state.phases[0].score_baseline

    for phase in state.phases:
        if phase.status == PhaseStatus.COMPLETED:
            total_score = phase.score_target
        elif phase.status == PhaseStatus.IN_PROGRESS:
            phase_progress = phase.calculate_progress() / 100.0
            score_increment = phase.score_target - phase.score_baseline
            total_score = phase.score_baseline + (phase_progress * score_increment)
            break

    return round(total_score, 1)

# --- REPORTING ---

def generate_progress_report(state: ProgressState, format: str = "text") -> str:
    """Generiert Fortschrittsbericht"""

    if format == "json":
        return json.dumps(asdict(state), indent=2, default=str)

    # Text-Report
    report = []
    report.append("=" * 80)
    report.append("Root24 Implementation Progress Report")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Week: {state.current_week} | Phase: {state.current_phase}/5")
    report.append("")

    # Overall Progress
    overall = state.calculate_overall_progress()
    report.append(f"📊 Overall Progress: {overall:.1f}%")
    report.append(f"🎯 Compliance Score: {state.current_score}/{state.target_score} ({state.current_score/state.target_score*100:.1f}%)")
    report.append("")

    # Status Indicators
    on_track = state.is_score_on_track()
    report.append(f"Status: {'✅ ON TRACK' if on_track else '⚠️  BEHIND TARGET'}")

    if not on_track:
        expected = state._calculate_expected_score()
        report.append(f"  Expected Score: {expected:.1f}")
        report.append(f"  Actual Score:   {state.current_score:.1f}")
        report.append(f"  Gap:            {expected - state.current_score:.1f} points")
    report.append("")

    # Phase Details
    report.append("📅 Phase Status:")
    report.append("")
    for phase in state.phases:
        status_icon = {
            PhaseStatus.NOT_STARTED: "⚪",
            PhaseStatus.IN_PROGRESS: "🔵",
            PhaseStatus.COMPLETED: "✅",
            PhaseStatus.BLOCKED: "🔴",
            PhaseStatus.AT_RISK: "⚠️"
        }.get(phase.status, "❓")

        phase_progress = phase.calculate_progress()
        report.append(f"{status_icon} Phase {phase.number}: {phase.name}")
        report.append(f"   Progress: {phase_progress:.1f}% | Score: {phase.score_baseline} → {phase.score_target}")
        report.append(f"   Timeline: Week {phase.week_start}-{phase.week_end}")

        # Critical KPIs
        critical_kpis = [kpi for kpi in phase.kpis if kpi.critical]
        if critical_kpis:
            report.append(f"   Critical KPIs:")
            for kpi in critical_kpis:
                pct = kpi.calculate_percentage()
                if pct is not None:
                    status = "✅" if pct >= 100 else "⚠️" if pct >= 80 else "❌"
                    report.append(f"     {status} {kpi.name}: {kpi.current}/{kpi.target} {kpi.unit} ({pct:.0f}%)")

        report.append("")

    # Risks & Recommendations
    report.append("🚨 Risks & Recommendations:")
    if not state.is_score_on_track():
        report.append("  • Score below target - prioritize MUST-requirements")
    if state.is_behind_schedule():
        report.append("  • Behind schedule - consider scope reduction for MAY-requirements")

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)

# --- MAIN ---

def main(output_format: str = "text"):
    """Hauptfunktion"""

    logger.info("Starting Progress Tracker")

    try:
        # Lade Konfiguration
        timeline = load_timeline_matrix()
        dashboard = load_dashboard_config()

        # Lade oder initialisiere State
        existing_state = load_progress_state()
        if existing_state:
            logger.info("Loading existing progress state")
            raise NotImplementedError("TODO: Implement this block")
            state = initialize_progress_state(timeline, dashboard)
        else:
            logger.info("Initializing new progress state")
            state = initialize_progress_state(timeline, dashboard)

        # Update Progress
        state = update_progress_from_sources(state)

        # Speichere State
        save_progress_state(state)

        # Generiere Report
        report = generate_progress_report(state, format=output_format)

        if output_format == "text":
            print(report)
        elif output_format == "json":
            print(report)

        # Exit Code basierend auf Status
        if not state.is_score_on_track():
            logger.warning("Progress behind target")
            return 1

        # Check kritische KPIs
        current_phase = state.phases[state.current_phase - 1]
        critical_failed = any(
            kpi.critical and (kpi.current or 0) < (kpi.target or 0)
            for kpi in current_phase.kpis
        )
        if critical_failed:
            logger.error("Critical KPI missed")
            return 2

        logger.info("Progress tracking completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        return 3

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Track Root24 implementation progress")
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    args = parser.parse_args()

    output_format = 'json' if args.json else args.format
    sys.exit(main(output_format=output_format))
