"""
Alerto QA Dashboard — Flask app for running Robot Framework tests by module
and streaming live output via Server-Sent Events.
"""

import os
import sys
import json
import uuid
import subprocess
import threading
import queue
import time
import glob
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Always use the same Python that launched this script so that installed
# packages (RequestsLibrary, SeleniumLibrary, etc.) are available to robot.
PYTHON_EXEC = sys.executable

# Paths
BASE_DIR = Path(__file__).parent.parent
TESTS_DIR = BASE_DIR / "tests"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

MODULES = [
    {"id": "AUTH",  "name": "Autenticación",     "file": "TC_AUTH.robot",   "tc_count": 13, "color": "#4A90D9", "req": "RF-009"},
    {"id": "UI",    "name": "Interfaz de Usuario","file": "TC_UI.robot",     "tc_count": 12, "color": "#7B68EE", "req": "RF-016"},
    {"id": "DATA",  "name": "Pipeline de Datos",  "file": "TC_DATA.robot",   "tc_count": 12, "color": "#20B2AA", "req": "RF-001..004"},
    {"id": "RISK",  "name": "Motor de Riesgo",    "file": "TC_RISK.robot",   "tc_count":  6, "color": "#FF8C00", "req": "RF-005,RF-010"},
    {"id": "ADMIN", "name": "Administración",     "file": "TC_ADMIN.robot",  "tc_count":  7, "color": "#CD853F", "req": "RF-015"},
    {"id": "SIM",   "name": "Simulador",          "file": "TC_SIM.robot",    "tc_count":  3, "color": "#32CD32", "req": "RF-002"},
    {"id": "ALERTS","name": "Alertas",            "file": "TC_ALERTS.robot", "tc_count":  3, "color": "#DC143C", "req": "RF-008"},
    {"id": "SEC",   "name": "Seguridad",          "file": "TC_SEC.robot",    "tc_count":  8, "color": "#8B0000", "req": "RF-009,RF-014"},
    {"id": "PERF",  "name": "Rendimiento",        "file": "TC_PERF.robot",   "tc_count":  4, "color": "#DAA520", "req": "RF-017,RF-018"},
    {"id": "INT",   "name": "Integración",        "file": "TC_INT.robot",    "tc_count":  4, "color": "#2E8B57", "req": "RF-001,RF-004"},
    {"id": "NOTIF", "name": "Notificaciones",     "file": "TC_NOTIF.robot",  "tc_count":  3, "color": "#FF69B4", "req": "RF-008"},
]

# In-memory job store
jobs: dict[str, dict] = {}
job_queues: dict[str, queue.Queue] = {}


def run_robot(job_id: str, module_id: str, test_file: str):
    """Run a Robot Framework test suite and stream output to a queue."""
    q = job_queues[job_id]
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = datetime.now().isoformat()

    output_dir = RESULTS_DIR / job_id
    output_dir.mkdir(exist_ok=True)

    cmd = [
        PYTHON_EXEC, "-m", "robot",
        "--outputdir", str(output_dir),
        "--output",   "output.xml",
        "--log",      "log.html",
        "--report",   "report.html",
        "--loglevel", "INFO",
        "--variable", f"SCREENSHOTS_DIR:{output_dir / 'screenshots'}",
        str(TESTS_DIR / test_file),
    ]

    q.put({"type": "start", "module": module_id, "cmd": " ".join(cmd)})

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(BASE_DIR),
        )
        jobs[job_id]["pid"] = proc.pid

        for line in proc.stdout:
            line = line.rstrip("\n")
            if line:
                q.put({"type": "log", "line": line})

        proc.wait()
        rc = proc.returncode
        jobs[job_id]["return_code"] = rc
        jobs[job_id]["status"] = "passed" if rc == 0 else "failed"

        # Parse result summary
        summary = parse_output_xml(output_dir / "output.xml")
        jobs[job_id]["summary"] = summary

        q.put({
            "type": "done",
            "return_code": rc,
            "status": jobs[job_id]["status"],
            "summary": summary,
            "report_url": f"/report/{job_id}",
        })

    except Exception as exc:
        jobs[job_id]["status"] = "error"
        q.put({"type": "error", "message": str(exc)})
    finally:
        jobs[job_id]["finished_at"] = datetime.now().isoformat()
        q.put(None)  # sentinel


def parse_output_xml(xml_path: Path) -> dict:
    """Extract pass/fail counts from Robot Framework output.xml."""
    summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    if not xml_path.exists():
        return summary
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_path)
        root = tree.getroot()
        stats = root.find(".//statistics/suite")
        if stats is None:
            stats = root.find(".//stat[@name]")
        # Try total stats
        total_stat = root.find(".//statistics/total/stat")
        if total_stat is not None:
            summary["passed"] = int(total_stat.get("pass", 0))
            summary["failed"] = int(total_stat.get("fail", 0))
            summary["skipped"] = int(total_stat.get("skip", 0))
            summary["total"] = summary["passed"] + summary["failed"] + summary["skipped"]
    except Exception:
        pass
    return summary


@app.route("/")
def index():
    return render_template("index.html", modules=MODULES)


@app.route("/api/modules")
def get_modules():
    result = []
    for m in MODULES:
        m_copy = dict(m)
        # Attach latest job info if any
        latest = None
        for jid, j in sorted(jobs.items(), key=lambda x: x[1].get("started_at", ""), reverse=True):
            if j.get("module_id") == m["id"]:
                latest = j
                break
        m_copy["last_job"] = latest
        result.append(m_copy)
    return jsonify(result)


@app.route("/api/run", methods=["POST"])
def run_tests():
    data = request.get_json() or {}
    module_id = data.get("module_id", "ALL")

    if module_id == "ALL":
        modules_to_run = MODULES
    else:
        modules_to_run = [m for m in MODULES if m["id"] == module_id]

    if not modules_to_run:
        return jsonify({"error": f"Module '{module_id}' not found"}), 404

    created_jobs = []
    for m in modules_to_run:
        job_id = str(uuid.uuid4())[:8]
        jobs[job_id] = {
            "job_id":    job_id,
            "module_id": m["id"],
            "module_name": m["name"],
            "status":    "queued",
            "started_at": None,
            "finished_at": None,
            "summary":   {},
        }
        job_queues[job_id] = queue.Queue()
        t = threading.Thread(target=run_robot, args=(job_id, m["id"], m["file"]), daemon=True)
        t.start()
        created_jobs.append(job_id)

    return jsonify({"jobs": created_jobs, "count": len(created_jobs)})


@app.route("/api/stream/<job_id>")
def stream(job_id):
    if job_id not in job_queues:
        return jsonify({"error": "Job not found"}), 404

    def generate():
        q = job_queues[job_id]
        while True:
            try:
                msg = q.get(timeout=30)
                if msg is None:
                    yield f"data: {json.dumps({'type': 'end'})}\n\n"
                    break
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/jobs")
def list_jobs():
    return jsonify(list(jobs.values()))


@app.route("/api/jobs/<job_id>")
def get_job(job_id):
    if job_id not in jobs:
        return jsonify({"error": "Not found"}), 404
    return jsonify(jobs[job_id])


@app.route("/report/<job_id>")
def serve_report(job_id):
    report_path = RESULTS_DIR / job_id / "report.html"
    if not report_path.exists():
        return "<h2>Report not yet available</h2>", 404
    return report_path.read_text(encoding="utf-8")


@app.route("/log/<job_id>")
def serve_log(job_id):
    log_path = RESULTS_DIR / job_id / "log.html"
    if not log_path.exists():
        return "<h2>Log not yet available</h2>", 404
    return log_path.read_text(encoding="utf-8")


@app.route("/api/reports")
def list_reports():
    reports = []
    for job_id, job in jobs.items():
        report_path = RESULTS_DIR / job_id / "report.html"
        reports.append({
            "job_id": job_id,
            "module_id": job.get("module_id"),
            "module_name": job.get("module_name"),
            "status": job.get("status"),
            "started_at": job.get("started_at"),
            "summary": job.get("summary", {}),
            "report_available": report_path.exists(),
        })
    return jsonify(reports)


@app.route("/api/install", methods=["POST"])
def install_deps():
    """Install/upgrade Robot Framework dependencies using the current Python."""
    req_file = BASE_DIR / "requirements.txt"
    cmd = [PYTHON_EXEC, "-m", "pip", "install", "-r", str(req_file), "--quiet"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        ok = result.returncode == 0
        return jsonify({
            "ok": ok,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


def check_robot_installed() -> bool:
    try:
        result = subprocess.run(
            [PYTHON_EXEC, "-m", "robot", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", 9090))
    print(f"\n{'='*60}")
    print(f"  Alerto QA Dashboard")
    print(f"  URL: http://localhost:{port}")
    print(f"  Python: {PYTHON_EXEC}")
    print(f"  Tests dir: {TESTS_DIR}")

    if not check_robot_installed():
        print("\n  [!] Robot Framework no encontrado. Instalando dependencias...")
        req_file = BASE_DIR / "requirements.txt"
        subprocess.run(
            [PYTHON_EXEC, "-m", "pip", "install", "-r", str(req_file), "-q"],
            timeout=180
        )
        if check_robot_installed():
            print("  [✓] Dependencias instaladas correctamente.")
        else:
            print("  [✗] No se pudieron instalar. Ejecuta install_deps.bat manualmente.")
    else:
        print("  [✓] Robot Framework disponible.")

    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
