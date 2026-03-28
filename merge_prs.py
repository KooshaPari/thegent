import subprocess
import json
import sys

# Excluded PRs
EXCLUDED = {
    "phenodocs": [9, 12, 15, 16],
    "helios-cli": [390]
}

def get_pr_details(repo_name_with_owner, pr_number):
    try:
        # number and url are standard fields in gh pr view --json
        cmd = [
            "gh", "pr", "view", str(pr_number),
            "--repo", repo_name_with_owner,
            "--json", "mergeStateStatus,mergeable,statusCheckRollup,number,url"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # print(f"Error command output for {repo_name_with_owner}#{pr_number}: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        # print(f"Error fetching PR {pr_number} from {repo_name_with_owner}: {e}")
        return None

def is_ci_green(pr_details):
    rollup = pr_details.get("statusCheckRollup")
    if not rollup:
        return True
    
    for check in rollup:
        typename = check.get("__typename")
        if typename == "CheckRun":
            status = check.get("status")
            conclusion = check.get("conclusion")
            if status != "COMPLETED":
                return False
            if conclusion not in ["SUCCESS", "SKIPPED", "NEUTRAL"]:
                return False
        elif typename == "StatusContext":
            state = check.get("state")
            if state != "SUCCESS":
                return False
    return True

def merge_pr(repo_name_with_owner, pr_number):
    print(f"Merging {repo_name_with_owner}#{pr_number}...")
    cmd = [
        "gh", "pr", "merge", str(pr_number),
        "--repo", repo_name_with_owner,
        "--merge", "--delete-branch"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully merged {repo_name_with_owner}#{pr_number}")
        return True
    else:
        print(f"Failed to merge {repo_name_with_owner}#{pr_number}: {result.stderr}")
        return False

def main():
    # Fetch all open PRs
    cmd = ["gh", "search", "prs", "--owner", "KooshaPari", "--state", "open", "--limit", "100", "--json", "number,repository"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error fetching PRs: {result.stderr}")
        return
    
    prs = json.loads(result.stdout)
    merged_list = []

    for i, pr in enumerate(prs):
        repo_name = pr["repository"]["name"]
        repo_full_name = pr["repository"]["nameWithOwner"]
        number = pr["number"]
        
        print(f"Processing {i+1}/{len(prs)}: {repo_full_name}#{number}...", flush=True)
        
        if repo_name in EXCLUDED and number in EXCLUDED[repo_name]:
            print(f"  Skipping excluded PR.", flush=True)
            continue
            
        details = get_pr_details(repo_full_name, number)
        if not details:
            continue
            
        mergeable = details.get("mergeable")
        merge_state = details.get("mergeStateStatus")
        
        if mergeable == "MERGEABLE" and merge_state == "CLEAN":
            if is_ci_green(details):
                if merge_pr(repo_full_name, number):
                    merged_list.append(f"{repo_full_name}#{number}")
            else:
                pass
                # print(f"CI not green for {repo_full_name}#{number}")
        else:
            pass
            # print(f"PR {repo_full_name}#{number} is not ready: {mergeable}/{merge_state}")

    if merged_list:
        print("\nMerged PRs summary:")
        for m in merged_list:
            print(f"- {m}")
    else:
        print("No PRs were merged.")

if __name__ == "__main__":
    main()
