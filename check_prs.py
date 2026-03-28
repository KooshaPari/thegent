import json
import subprocess
import sys

def get_pr_status(repo, pr_numbers):
    ready_to_merge = []
    failing = []
    
    for num in pr_numbers:
        try:
            cmd = ["gh", "pr", "view", str(num), "--repo", repo, "--json", "number,title,mergeable,statusCheckRollup,state"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            if data["state"] != "OPEN":
                continue
                
            checks = data.get("statusCheckRollup", [])
            all_success = True
            for check in checks:
                # Some might be in progress or queued
                status = check.get("status")
                conclusion = check.get("conclusion")
                state = check.get("state") # for StatusContext
                
                if status == "COMPLETED":
                    if conclusion != "SUCCESS" and conclusion != "SKIPPED":
                        all_success = False
                        break
                elif state: # StatusContext (like CodeRabbit)
                    if state != "SUCCESS":
                        all_success = False
                        break
                else:
                    # QUEUED or IN_PROGRESS or PENDING
                    all_success = False
                    break
            
            if data["mergeable"] == "MERGEABLE" and all_success and checks:
                ready_to_merge.append(data)
            elif any(c.get("conclusion") == "FAILURE" or c.get("state") == "FAILURE" for c in checks):
                failing.append(data)
            else:
                # Might be pending or no checks
                pass
                
        except Exception as e:
            print(f"Error checking PR {num}: {e}", file=sys.stderr)
            
    return ready_to_merge, failing

if __name__ == "__main__":
    repo = "KooshaPari/helios-cli"
    # List of PR numbers from search results
    pr_numbers = [482, 481, 480, 479, 477, 476, 475, 474, 473, 472, 469, 463, 460, 459, 458, 455, 454, 452, 450, 449, 448, 446, 445, 444, 443, 442, 441, 440, 437, 436, 435, 434, 433, 432, 427, 424, 423, 422, 417, 416, 415, 414, 411, 409, 408, 407, 406, 405, 404, 403, 401, 400]
    
    ready, failing = get_pr_status(repo, pr_numbers)
    
    print(json.dumps({"ready": ready, "failing": failing}, indent=2))
