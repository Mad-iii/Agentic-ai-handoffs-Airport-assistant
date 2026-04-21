#!/usr/bin/env python3
import sys
import subprocess
import os

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "handsoffsample.py":
        # Run the handsoffsample module
        subprocess.run([sys.executable, "-m", "basichandoffs.handsoffsample"])
    else:
        print("Usage: uv run basic handsoffsample.py")
        print("This will run the handsoffsample module")

if __name__ == "__main__":
    main() 