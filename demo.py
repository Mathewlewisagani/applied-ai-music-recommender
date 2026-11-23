#!/usr/bin/env python3
"""
VibeCheck 2.0 Unified Launcher & Demo.
Provides multiple ways to inspect, test, and experience the Applied AI Recommender System.

Usage:
    python3 demo.py              # Launches Friendly Streamlit App (Default)
    streamlit run app.py         # Direct Streamlit launch
    python3 demo.py --benchmark  # Runs V1.0 vs V2.0 quantitative metric evaluation
    python3 demo.py --test       # Runs full verification test suite
    python3 demo.py --cli        # Terminal CLI mode
    python3 demo.py --web        # Zero-dependency local web server
"""

import sys
import os
import subprocess
import shutil

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def find_streamlit_bin():
    candidates = [
        "/tmp/music_venv/bin/streamlit",
        shutil.which("streamlit"),
        os.path.expanduser("~/.local/bin/streamlit"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def launch_streamlit(port=8501):
    st_bin = find_streamlit_bin()
    app_path = os.path.join(root_dir, "app.py")
    if not st_bin:
        print("Streamlit binary not found. Launching built-in web server instead...")
        from applied_ai_recommender.ui.web_server import start_server
        start_server(port=8080)
        return

    print(f"\n🎧 Launching VibeCheck 2.0 Friendly Streamlit App...")
    print(f"👉 Opening at: http://localhost:{port}\n")
    cmd = [st_bin, "run", app_path, f"--server.port={port}", "--server.headless=true"]
    subprocess.run(cmd)


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "--streamlit"

    if mode in ["--streamlit", "-s"]:
        port = int(args[1]) if len(args) > 1 else 8501
        launch_streamlit(port)

    elif mode in ["--cli", "-c"]:
        from applied_ai_recommender.ui.cli import run_cli_interactive
        run_cli_interactive()

    elif mode in ["--benchmark", "-b"]:
        from applied_ai_recommender.evaluation.benchmark import print_benchmark_summary
        print_benchmark_summary()

    elif mode in ["--web", "-w"]:
        from applied_ai_recommender.ui.web_server import start_server
        port = 8080
        if len(args) > 1:
            try:
                port = int(args[1])
            except ValueError:
                pass
        start_server(port)

    elif mode in ["--test", "-t"]:
        from applied_ai_recommender.tests.run_all_tests import run_tests
        success = run_tests()
        sys.exit(0 if success else 1)

    else:
        # Default fallback to Streamlit
        launch_streamlit()


if __name__ == "__main__":
    main()
