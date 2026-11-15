# push_to_git.py - 1-Click GitHub Remote Sync Tool for Anvil Breaker™
import sys
import os
import subprocess
import shutil

PORTABLE_GIT = r"C:\paypal hacketon\git_bin\cmd\git.exe"

def get_git_cmd():
    if os.path.exists(PORTABLE_GIT):
        return PORTABLE_GIT
    cmd = shutil.which("git")
    if cmd:
        return cmd
    return None

def main():
    repo_path = os.path.abspath(os.path.dirname(__file__))
    
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("⚒️  ANVIL BREAKER™ — 1-CLICK GITHUB & RENDER DEPLOYER")
        print("="*60)
        print("Author: Mustafa Marjani <founder@anvilbreaker.dev>")
        print("\nUsage: python push_to_git.py <GITHUB_REPO_URL>")
        print("Example:")
        print("  python push_to_git.py https://github.com/mustafa64-stack/anvil-breaker.git")
        print("Or if using a GitHub Personal Access Token (PAT):")
        print("  python push_to_git.py https://ghp_YOURTOKEN@github.com/mustafa64-stack/anvil-breaker.git\n")
        print("Render 1-Click Deployment URL:")
        print("  https://render.com/deploy?repo=https://github.com/mustafa64-stack/anvil-breaker\n")
        return

    remote_url = sys.argv[1].strip()
    git_bin = get_git_cmd()

    print(f"\n[1/3] Configuring remote origin -> {remote_url}...")
    if git_bin:
        # Check if origin already exists
        remotes = subprocess.run([git_bin, "-C", repo_path, "remote"], capture_output=True, text=True).stdout.split()
        if "origin" in remotes:
            subprocess.run([git_bin, "-C", repo_path, "remote", "set-url", "origin", remote_url], check=True)
        else:
            subprocess.run([git_bin, "-C", repo_path, "remote", "add", "origin", remote_url], check=True)
        
        # Ensure default branch is main
        subprocess.run([git_bin, "-C", repo_path, "branch", "-M", "main"], check=True)
        
        print("[2/3] Staging and committing all updates...")
        subprocess.run([git_bin, "-C", repo_path, "add", "."], check=True)
        subprocess.run([git_bin, "-C", repo_path, "commit", "-m", "chore: sync Anvil Breaker deployment build", "--allow-empty"], check=True)

        print(f"[3/3] Pushing to GitHub (main branch)...")
        push_res = subprocess.run([git_bin, "-C", repo_path, "push", "-u", "origin", "main"], capture_output=True, text=True)
        if push_res.returncode == 0:
            print("\n" + "="*60)
            print("🚀 SUCCESS! Repository pushed to GitHub!")
            print("="*60)
            clean_repo = remote_url.replace(".git", "").split("@")[-1]
            if not clean_repo.startswith("https://"):
                clean_repo = "https://" + clean_repo
            print(f"\n👉 1-Click Render Deploy Link:")
            print(f"   https://render.com/deploy?repo={clean_repo}")
            print("\nClicking that link deploys anvil-breaker to:")
            print("   👉 https://anvil-breaker.onrender.com\n")
        else:
            print(f"\n❌ Git Push output:\n{push_res.stderr}\n{push_res.stdout}")
            if "Authentication failed" in push_res.stderr or "could not read Username" in push_res.stderr:
                print("Tip: Provide your GitHub PAT directly in the URL:")
                print("  python push_to_git.py https://ghp_YOURTOKEN@github.com/mustafa64-stack/anvil-breaker.git\n")
    else:
        # Fallback to dulwich
        from dulwich import porcelain
        try:
            porcelain.remote_add(repo_path, 'origin', remote_url)
        except Exception:
            pass
        porcelain.add(repo_path, '.')
        try:
            porcelain.commit(repo_path, message=b"chore: sync Anvil Breaker release", author=b"Mustafa Marjani <founder@anvilbreaker.dev>")
        except Exception:
            pass
        porcelain.push(repo_path, remote_url, refspecs=[b'refs/heads/main:refs/heads/main'])
        print("\n🚀 Pushed successfully via Dulwich!")

if __name__ == "__main__":
    main()
