from src.ui.cli import main as cli_main
from src.ui.streamlit_app import run_app as run_streamlit
from src.ui.gradio_app import launch_app as run_gradio
import argparse

def parse_args():
    p = argparse.ArgumentParser(description="AI Fact-Checker Bot entry point")
    p.add_argument("--mode", choices=["cli","streamlit","gradio"], default="cli")
    p.add_argument("--claim", type=str, help="Claim to fact-check (CLI mode)")
    return p.parse_args()

def main():
    args = parse_args()
    if args.mode == "cli":
        cli_main(args.claim)
    elif args.mode == "streamlit":
        run_streamlit()
    else:
        run_gradio()

if __name__ == "__main__":
    main()
