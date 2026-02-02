import requests
from collections import defaultdict
import matplotlib.pyplot as plt
import datetime

def analyze_github_activity(username_or_org, is_org=False, num_days=30):
    """
    Analyzes GitHub repository activity for a given user or organization.

    Args:
        username_or_org (str): The GitHub username or organization name.
        is_org (bool): True if analyzing an organization, False for a user.
        num_days (int): The number of past days to consider for activity.

    Returns:
        dict: A dictionary containing the summary report.
    """
    report = {
        "username_or_org": username_or_org,
        "is_org": is_org,
        "num_days": num_days,
        "total_commits": 0,
        "total_issues_opened": 0,
        "total_issues_closed": 0,
        "total_pull_requests_opened": 0,
        "total_pull_requests_merged": 0,
        "repositories": {},
        "activity_over_time": defaultdict(int)
    }

    api_base_url = "https://api.github.com"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    if is_org:
        # Get repositories for the organization
        url = f"{api_base_url}/orgs/{username_or_org}/repos"
    else:
        # Get repositories for the user
        url = f"{api_base_url}/users/{username_or_org}/repos"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repositories: {e}")
        return None

    if not repos:
        print(f"No repositories found for {username_or_org}.")
        return report

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=num_days)

    for repo in repos:
        repo_name = repo["name"]
        report["repositories"][repo_name] = {
            "commits": 0,
            "issues_opened": 0,
            "issues_closed": 0,
            "pull_requests_opened": 0,
            "pull_requests_merged": 0
        }

        # Analyze commits
        commits_url = f"{api_base_url}/repos/{username_or_org}/{repo_name}/commits"
        try:
            commits_response = requests.get(commits_url, headers=headers, params={"since": start_date.isoformat()})
            commits_response.raise_for_status()
            commits = commits_response.json()
            for commit in commits:
                if commit['author'] and commit['author']['login'] == username_or_org or not is_org: # Basic check, could be improved
                    report["total_commits"] += 1
                    report["repositories"][repo_name]["commits"] += 1
                    commit_date = datetime.datetime.fromisoformat(commit['commit']['author']['date'].replace('Z', '+00:00'))
                    if start_date <= commit_date <= end_date:
                        report["activity_over_time"][commit_date.strftime('%Y-%m-%d')] += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commits for {repo_name}: {e}")

        # Analyze issues
        issues_url = f"{api_base_url}/repos/{username_or_org}/{repo_name}/issues"
        try:
            issues_response = requests.get(issues_url, headers=headers, params={"state": "all"})
            issues_response.raise_for_status()
            issues = issues_response.json()
            for issue in issues:
                # Exclude pull requests from issue count
                if "pull_request" in issue:
                    continue

                issue_date = datetime.datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                if start_date <= issue_date <= end_date:
                    if issue['state'] == 'open':
                        report["total_issues_opened"] += 1
                        report["repositories"][repo_name]["issues_opened"] += 1
                        report["activity_over_time"][issue_date.strftime('%Y-%m-%d')] += 1
                    elif issue['state'] == 'closed':
                        report["total_issues_closed"] += 1
                        report["repositories"][repo_name]["issues_closed"] += 1
                        report["activity_over_time"][issue_date.strftime('%Y-%m-%d')] += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues for {repo_name}: {e}")

        # Analyze pull requests
        pulls_url = f"{api_base_url}/repos/{username_or_org}/{repo_name}/pulls"
        try:
            pulls_response = requests.get(pulls_url, headers=headers, params={"state": "all"})
            pulls_response.raise_for_status()
            pulls = pulls_response.json()
            for pull in pulls:
                pull_date = datetime.datetime.fromisoformat(pull['created_at'].replace('Z', '+00:00'))
                if start_date <= pull_date <= end_date:
                    if pull['state'] == 'open':
                        report["total_pull_requests_opened"] += 1
                        report["repositories"][repo_name]["pull_requests_opened"] += 1
                        report["activity_over_time"][pull_date.strftime('%Y-%m-%d')] += 1
                    elif pull['state'] == 'closed':
                        # Check if it was merged
                        if pull['merged_at']:
                            report["total_pull_requests_merged"] += 1
                            report["repositories"][repo_name]["pull_requests_merged"] += 1
                            report["activity_over_time"][pull_date.strftime('%Y-%m-%d')] += 1
                        else:
                            report["repositories"][repo_name]["pull_requests_opened"] += 1 # Count closed without merge as opened initially
                            report["activity_over_time"][pull_date.strftime('%Y-%m-%d')] += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching pull requests for {repo_name}: {e}")

    return report

def print_summary_report(report):
    """Prints a formatted summary report."""
    if not report:
        return

    print("\n--- GitHub Activity Summary Report ---")
    print(f"Target: {report['username_or_org']} ({'Organization' if report['is_org'] else 'User'})")
    print(f"Timeframe: Last {report['num_days']} days")
    print("--------------------------------------")
    print(f"Total Commits: {report['total_commits']}")
    print(f"Total Issues Opened: {report['total_issues_opened']}")
    print(f"Total Issues Closed: {report['total_issues_closed']}")
    print(f"Total Pull Requests Opened: {report['total_pull_requests_opened']}")
    print(f"Total Pull Requests Merged: {report['total_pull_requests_merged']}")
    print("--------------------------------------")
    print("Activity by Repository:")
    if report["repositories"]:
        for repo, data in report["repositories"].items():
            print(f"  - {repo}:")
            print(f"    Commits: {data['commits']}")
            print(f"    Issues Opened: {data['issues_opened']}")
            print(f"    Issues Closed: {data['issues_closed']}")
            print(f"    Pull Requests Opened: {data['pull_requests_opened']}")
            print(f"    Pull Requests Merged: {data['pull_requests_merged']}")
    else:
        print("  No repository activity found.")
    print("--------------------------------------")

def visualize_activity(report):
    """Generates a bar chart for daily activity."""
    if not report or not report["activity_over_time"]:
        print("No activity data to visualize.")
        return

    dates = sorted(report["activity_over_time"].keys())
    activities = [report["activity_over_time"][date] for date in dates]

    plt.figure(figsize=(12, 6))
    plt.bar(dates, activities, color='skyblue')
    plt.xlabel("Date")
    plt.ylabel("Activity Count")
    plt.title(f"Daily GitHub Activity for {report['username_or_org']} (Last {report['num_days']} days)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # --- Configuration ---
    GITHUB_USER_OR_ORG = "octocat"  # Replace with a GitHub username or organization name
    IS_ORGANIZATION = False         # Set to True if GITHUB_USER_OR_ORG is an organization
    DAYS_TO_ANALYZE = 30            # Number of past days to analyze
    # ---------------------

    github_report = analyze_github_activity(GITHUB_USER_OR_ORG, is_org=IS_ORGANIZATION, num_days=DAYS_TO_ANALYZE)

    if github_report:
        print_summary_report(github_report)
        visualize_activity(github_report)
