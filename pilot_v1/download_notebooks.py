import re
import os
import subprocess

def main():
    links_file = "/usr/local/google/home/nicholaskang/benchmarks-auto-scoring/pilot_v1/agi_hackathon_benchmark_links.md"
    with open(links_file, "r") as f:
        content = f.read()

    # Split by the markdown line separator "---"
    entries = content.split("\n---\n")
    
    for entry in entries:
        if not entry.strip():
            continue
        
        # Get writeup URL / slug
        writeup_match = re.search(r'Writeup URL:\*\* \[[a-zA-Z0-9\-]+\]\(https://www.kaggle.com/competitions/kaggle-measuring-agi/writeups/([a-zA-Z0-9\-]+)\)', entry)
        if not writeup_match:
            continue
        
        writeup_slug = writeup_match.group(1)
        print(f"\nProcessing benchmark writeup slug: {writeup_slug}")
        
        # Find all Notebook URLs in this entry
        # Format: [Notebook](https://www.kaggle.com/code/owner/kernel-slug)
        notebook_urls = re.findall(r'\[Notebook\]\(https://www.kaggle.com/code/([a-zA-Z0-9\-\_]+)/([a-zA-Z0-9\-\_]+)\)', entry)
        
        if not notebook_urls:
            print("  No public notebook URLs found.")
            continue
            
        target_dir = f"/tmp/benchmarks_backtest/{writeup_slug}/notebooks"
        os.makedirs(target_dir, exist_ok=True)
        
        for owner, kernel_slug in notebook_urls:
            kernel_spec = f"{owner}/{kernel_slug}"
            print(f"  Pulling kernel: {kernel_spec} -> {target_dir}")
            
            # Run kaggle kernels pull
            cmd = [
                "/usr/local/google/home/nicholaskang/kaggle-cli-venv/bin/kaggle",
                "kernels",
                "pull",
                kernel_spec,
                "-p",
                target_dir
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    print(f"    Success: {res.stdout.strip()}")
                else:
                    print(f"    Failed to pull {kernel_spec}: {res.stderr.strip()}")
            except Exception as e:
                print(f"    Exception trying to pull {kernel_spec}: {str(e)}")

if __name__ == "__main__":
    main()
