import requests
from datetime import datetime
import requests
from git import Repo
import os

def get_workflow_id(token, repo, workflow_name):
    """Fetch the numeric workflow ID from GitHub API based on the workflow name."""
    url = f"https://api.github.com/repos/{repo}/actions/workflows"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        workflows = response.json().get("workflows", [])
        for workflow in workflows:
            if workflow["name"] == workflow_name:
                return workflow["id"]  # Return the numeric workflow ID
        raise ValueError(f"Workflow '{workflow_name}' not found in repository {repo}.")
    else:
        raise Exception(f"Failed to fetch workflows: {response.status_code} - {response.text}")

def no_other_workflows_running(token, github_repo, workflow_id, run_id):
    url = f"https://api.github.com/repos/{github_repo}/actions/workflows/{workflow_id}/runs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "status": "in_progress"  # Fetch only workflows that are currently running
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        runs = data.get("workflow_runs", [])
        
        # Filter out the current workflow run
        filtered_runs = [run for run in runs if str(run["id"]) != run_id]
        
        # If no other workflows are running, return True
        if not filtered_runs:
            return True, None
        else:
            result = f"Found {len(filtered_runs)} older running workflows:"
            for run in filtered_runs:
                created_at = datetime.strptime(run["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                result += f"\n- ID: {run['id']}, Created At: {created_at}, URL: {run['html_url']}"
            return False, result
    else:
        return False, f"Failed to fetch workflow runs: {response.status_code} - {response.text}"

import shutil
import string
import random

def generate_hidden_branch():
    randchars = []
    characterList = string.ascii_letters + string.digits
    for i in range(20):
        randchars.append(random.choice(characterList))
    return "hidden/" + "".join(randchars)

def upload_file(token, repo, file, branch, rename = None, tempdir = "__tmp__"):
    # Create a temporary directory for the branch
    repo_dir = f'./{tempdir}/{repo}'
    branch_dir = os.path.join(repo_dir, branch)
    
    # Clone the repo into a new folder if it doesn't exist
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
        repo_instance = Repo.clone_from(f'https://github-actions:{token}@github.com/{repo}.git', repo_dir)
    else:
        # If it exists, use the existing directory
        print(f"Directory {repo_dir} exists, using it for the repository.")
        repo_instance = Repo(repo_dir)
    origin = repo_instance.remote(name="origin")
    origin.fetch()

    # Fetch all remote branches to make sure we have the latest refs
    repo_instance.git.fetch('--all')

    try:
        origin.pull(branch)
    except Exception:
        pass

    # Check if the branch exists locally, if not, check it out from the remote
    try:
        if branch not in [b.name for b in repo_instance.branches]:
            print(f"Branch {branch} does not exist locally. Checking it out from remote.")
            # Check out the remote branch (this will create a local tracking branch)
            repo_instance.git.checkout(f'origin/{branch}', b=branch)
            origin.pull(branch)
    except Exception:
        pass

    if branch not in repo_instance.branches:
        print(f"Branch {branch} does not exist. Creating an orphan branch.")
        repo_instance.git.checkout('--orphan', branch)
        repo_instance.git.reset('--hard')

        # Make an empty commit so that the branch is recognized by git
        repo_instance.index.commit("Initial empty commit on orphan branch")
        
        # Push the new branch to the remote repository
        origin = repo_instance.remote(name='origin')
        origin.push(branch)
        print(f"Branch {branch} created and pushed to remote repository.")

    # Checkout the target branch
    repo_instance.git.checkout(branch)

    # Copy the file directly to the root of the branch
    if rename == None:
        rename = os.path.basename(file)
        dest = os.path.join(repo_dir, rename)
    else:
        rename = rename.lstrip("/")
        dest = os.path.join(repo_dir, rename)
        dir_of_dest = os.path.dirname(dest)
        if not os.path.exists(dir_of_dest):
            os.makedirs(dir_of_dest)

    if os.path.isdir(file):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(file, dest)
    else:
        shutil.copy(file, dest)

    # Stage the file for commit
    repo_instance.git.add(rename)

   # Commit the file
    repo_instance.index.commit(f"Add {file} to {branch} branch")

    # Force push the changes (to overwrite any conflicting changes in the remote branch)
    origin = repo_instance.remote(name='origin')
    origin.push(branch, force=True)  # Force push the branch to the remote repository

    full_sha = repo_instance.head.object.hexsha

    if branch.startswith("hidden/"):
        origin.push(branch, delete=True)
        print(f"Branch {branch} deleted from remote repository.")

    return full_sha

def github_url_of_raw(repo, file, branch):
    return f'https://raw.githubusercontent.com/{repo}/{branch}/{file}'

def get_raw_file(url, outfile):
    # Ensure the output directory exists
    outfile = os.path.abspath(outfile)
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    
    # Send the GET request to GitHub API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Return the raw content of the file
        with open(outfile, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Write only non-empty chunks
                    f.write(chunk)
    else:
        # Handle the error if the file is not found or any other issue
        raise Exception(f"Failed to fetch file: {response.status_code} - {response.text}")

def get_file(token, repo, file, branch, outfile):
    # GitHub API URL to get the raw file content
    url = f'https://api.github.com/repos/{repo}/contents/{file}?ref={branch}'

    # Ensure the output directory exists
    outfile = os.path.abspath(outfile)
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    
    # Set up the headers with the token for authentication
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3.raw',  # Ensure we get the raw content
    }
    
    # Send the GET request to GitHub API
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Return the raw content of the file
        with open(outfile, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Write only non-empty chunks
                    f.write(chunk)
    else:
        # Handle the error if the file is not found or any other issue
        raise Exception(f"Failed to fetch file: {response.status_code} - {response.text}")
