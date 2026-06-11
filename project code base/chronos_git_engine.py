import collections
import itertools
import json
import os
import subprocess


def generate_mock_git_history():
    """Generates a realistic mock commit history for an e-commerce platform

    if no real Git repository is detected.
    """
    print("[!] No active Git repository detected. Initializing synthetic history...")
    # Simulating file changes per commit
    mock_commits = [
        {"auth.py", "jwt.py", "database.py"},
        {"auth.py", "billing.py", "user_repo.py"},
        {"auth.py", "billing.py"},
        {"database.py", "user_repo.py"},
        {"database.py", "user_repo.py", "product_catalog.py"},
        {"cache.py", "session.py"},
        {"cache.py", "session.py", "auth.py"},
        {"billing.py", "payment_gateway.py"},
        {"billing.py", "payment_gateway.py", "user_repo.py"},
        {"cache.py", "session.py"},
    ]
    return mock_commits
def extract_git_commits(repo_path):
    """Executes git log to retrieve a list of files modified in each commit."""
    if not os.path.exists(os.path.join(repo_path, ".git")):
        return generate_mock_git_history()

    # Limit git log output to the last 150 commits to prevent locking on large repos
    cmd = ["git", "log", "-n", "150", "--pretty=format:commit:%H", "--name-only"]
    try:
        import subprocess
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5
        )
        if result.returncode != 0:
            print(f"[-] Git log command failed with code {result.returncode}. Falling back to synthetic history.")
            return generate_mock_git_history()
    except subprocess.TimeoutExpired:
        print("[-] Git log command timed out. Falling back to synthetic history.")
        return generate_mock_git_history()
    except Exception as e:
        print(f"[-] Git extraction failed: {e}. Falling back to synthetic history.")
        return generate_mock_git_history()

    commits = []
    current_commit_files = set()

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("commit:"):
            if current_commit_files:
                commits.append(current_commit_files)
                current_commit_files = set()
        else:
            if any(
                line.endswith(ext)
                for ext in [".py", ".js", ".ts", ".go", ".java", ".cpp", ".cs"]
            ):
                current_commit_files.add(line)

    if current_commit_files:
        commits.append(current_commit_files)

    if not commits:
        print("[!] No commit history extracted. Falling back to synthetic history.")
        return generate_mock_git_history()

    return commits


def calculate_temporal_coupling(commits, min_commit_threshold=2):
    """Computes directional co-change matrices based on commit history."""
    file_commit_counts = collections.Counter()
    co_occurrence_counts = collections.defaultdict(collections.Counter)

    for commit_files in commits:
        for file in commit_files:
            file_commit_counts[file] += 1

        for file_a, file_b in itertools.combinations(commit_files, 2):
            co_occurrence_counts[file_a][file_b] += 1
            co_occurrence_counts[file_b][file_a] += 1

    temporal_matrix = {}

    for file_i, total_commits_i in file_commit_counts.items():
        if total_commits_i < min_commit_threshold:
            continue

        temporal_matrix[file_i] = {}
        for file_j, joint_count in co_occurrence_counts[file_i].items():
            probability = round(joint_count / total_commits_i, 2)
            if probability > 0.1:
                temporal_matrix[file_i][file_j] = probability

        if not temporal_matrix[file_i]:
            del temporal_matrix[file_i]

    return temporal_matrix


if __name__ == "__main__":
    TARGET_REPO = "./"
    print(f"[*] Chronos Engine Initializing: Scanning {TARGET_REPO}...")

    raw_history = extract_git_commits(TARGET_REPO)
    print(f"[+] Processed {len(raw_history)} historical commits.")

    matrix = calculate_temporal_coupling(raw_history, min_commit_threshold=2)

    print("\n[+] Target Milestone Achieved. Temporal Matrix Generated:\n")
    print(json.dumps(matrix, indent=2))

    with open("chronos_git_matrix.json", "w") as f:
        json.dump(matrix, f, indent=2)