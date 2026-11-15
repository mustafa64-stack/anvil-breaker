# push_to_git.py - 1-Click GitHub Remote Sync Tool
import sys
import os
from dulwich import porcelain

def main():
    if len(sys.argv) < 2:
        print("\n⚒️  Anvil Breaker™ — Git Remote Pusher")
        print("Usage: python push_to_git.py <GITHUB_REPO_URL>")
        print("Example: python push_to_git.py https://github.com/yourusername/anvil-breaker.git\n")
        return

    remote_url = sys.argv[1].strip()
    repo_path = '.'
    
    print(f"Adding remote 'origin' -> {remote_url}...")
    try:
        porcelain.remote_add(repo_path, 'origin', remote_url)
    except Exception:
        # Remote may already exist
        pass

    print("Staging latest changes...")
    porcelain.add(repo_path, '.')

    try:
        porcelain.commit(
            repo_path,
            message=b"update: latest Anvil Breaker enhancements",
            author=b"Mustafa Marjani <founder@anvilbreaker.dev>"
        )
    except Exception:
        print("Working tree clean, no new commit needed.")

    print(f"Pushing to {remote_url} (main branch)...")
    try:
        porcelain.push(repo_path, remote_url, refspecs=[b'refs/heads/master:refs/heads/main'])
        print("\n🚀 Successfully pushed to your GitHub repository!")
    except Exception as e:
        print(f"\nNote: If GitHub requires authentication, push via GitHub Desktop or personal access token: {e}")

if __name__ == "__main__":
    main()

