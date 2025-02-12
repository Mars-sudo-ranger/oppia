import os
import sys
import requests

def main():
    if len(sys.argv) != 3:
        print("Usage: python check_membership.py <org> <team_slug>")
        sys.exit(1)

    org = sys.argv[1]
    team_slug = sys.argv[2]
    user = os.environ.get("GITHUB_ACTOR")
    if not user:
        print("Error: GITHUB_ACTOR environment variable is not set.")
        sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # This query looks up the specified team (by slug) in the organization and
    # returns the total count of members whose login matches the given user.
    query = """
    query($org: String!, $teamSlug: String!, $userLogin: String!) {
      organization(login: $org) {
        team(slug: $teamSlug) {
          members(query: $userLogin, first: 1) {
            totalCount
          }
        }
      }
    }
    """

    variables = {
        "org": org,
        "teamSlug": team_slug,
        "userLogin": user
    }

    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code} - {response.text}")
        sys.exit(1)

    data = response.json()
    if "errors" in data:
        print("GraphQL errors:")
        for error in data["errors"]:
            print(error["message"])
        sys.exit(1)

    # If the team is not found, data["data"]["organization"]["team"] will be None.
    team_data = data.get("data", {}).get("organization", {}).get("team")
    if team_data is None:
        print(f"Error: Team '{team_slug}' not found in organization '{org}'.")
        sys.exit(1)

    total_count = team_data.get("members", {}).get("totalCount", 0)
    if total_count > 0:
        print(f"User '{user}' is a member of team '{team_slug}' in organization '{org}'.")
        sys.exit(0)
    else:
        print(f"User '{user}' is NOT a member of team '{team_slug}' in organization '{org}'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
