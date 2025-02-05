#!/usr/bin/env python3
import os
import sys
import requests
import json

def main():
    # The script now expects only two command-line arguments:
    # the organization login and the team slug.
    if len(sys.argv) != 3:
        print("Usage: python check_membership.py <org> <team_slug>")
        sys.exit(1)

    org = sys.argv[1]         # e.g., "oppia"
    team_slug = sys.argv[2]    # e.g., "oppia-good-first-issue-labelers"

    # Instead of passing the username as an argument, read it from the environment.
    user = os.environ.get("GITHUB_ACTOR")
    if not user:
        print("Error: GITHUB_ACTOR environment variable is not set. Run this script within GitHub Actions or pass the username explicitly.")
        sys.exit(1)

    # Get the GitHub token from environment variables.
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: Please set the GITHUB_TOKEN environment variable with your GitHub API token.")
        sys.exit(1)

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # GraphQL query to check team membership for a user.
    query = """
    query($org: String!, $teamSlug: String!, $user: String!) {
      organization(login: $org) {
        team(slug: $teamSlug) {
          membershipForUser(login: $user) {
            role
          }
        }
      }
    }
    """

    variables = {
        "org": org,
        "teamSlug": team_slug,
        "user": user
    }

    print(f"Querying membership for user '{user}' in team '{team_slug}' within organization '{org}'...")

    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code} - {response.text}")
        sys.exit(1)
    
    data = response.json()
    
    # Check if there are GraphQL errors
    if "errors" in data:
        print("GraphQL errors:")
        print(json.dumps(data["errors"], indent=2))
        sys.exit(1)
    
    # Navigate the returned JSON structure.
    organization = data.get("data", {}).get("organization")
    if organization is None:
        print(f"Error: Organization '{org}' not found.")
        sys.exit(1)
    
    team = organization.get("team")
    if team is None:
        print(f"Error: Team '{team_slug}' not found in organization '{org}'.")
        sys.exit(1)
    
    membership = team.get("membershipForUser")
    if membership:
        print(f"User '{user}' is a member of team '{team_slug}' with role: {membership['role']}")
    else:
        print(f"User '{user}' is NOT a member of team '{team_slug}' in organization '{org}'.")

if __name__ == '__main__':
    main()
