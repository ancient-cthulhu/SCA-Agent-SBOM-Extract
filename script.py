import os
import argparse
import requests
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC

BASE_URL = "https://api.veracode.com"

def sanitize(name):
    return name.replace("/", "_").replace("\\", "_").strip()

def get_workspaces(session):
    url = f"{BASE_URL}/srcclr/v3/workspaces"
    r = session.get(url)
    r.raise_for_status()
    data = r.json()
    
    if "_embedded" in data and "workspaces" in data["_embedded"]:
        return data["_embedded"]["workspaces"]
    elif "workspaces" in data:
        return data["workspaces"]
    else:
        return []

def get_projects(session, workspace_guid):
    url = f"{BASE_URL}/srcclr/v3/workspaces/{workspace_guid}/projects"
    r = session.get(url)
    r.raise_for_status()
    data = r.json()
    
    if "_embedded" in data and "projects" in data["_embedded"]:
        return data["_embedded"]["projects"]
    elif "projects" in data:
        return data["projects"]
    else:
        return []

def get_sbom(session, project_guid, include_vulns, sbom_format="cyclonedx"):
    vuln_param = "" if include_vulns else "&vulnerability=false"
    url = f"{BASE_URL}/srcclr/sbom/v1/targets/{project_guid}/{sbom_format}?type=agent{vuln_param}"
    r = session.get(url)

    if r.status_code == 404:
        return None

    r.raise_for_status()
    return r.text

def main():

    parser = argparse.ArgumentParser(description="Export Veracode SCA SBOMs")
    parser.add_argument("--output-dir", default="sboms")
    parser.add_argument("--vulns", action="store_true", help="Include vulnerabilities in SBOM")
    parser.add_argument("--format", default="cyclonedx", choices=["cyclonedx", "spdx"], 
                        help="SBOM format type (default: cyclonedx)")
    args = parser.parse_args()

    session = requests.Session()
    session.auth = RequestsAuthPluginVeracodeHMAC()

    os.makedirs(args.output_dir, exist_ok=True)

    print("Fetching workspaces...")
    workspaces = get_workspaces(session)

    for ws in workspaces:

        ws_name = sanitize(ws["name"])
        
        ws_guid = ws.get("guid") or ws.get("id") or ws.get("workspace_id")
        
        if not ws_guid and "_links" in ws and "self" in ws["_links"]:
            href = ws["_links"]["self"]["href"]
            ws_guid = href.split("/")[-1]
        
        if not ws_guid:
            print(f"  ERROR: Could not find workspace GUID for '{ws_name}'. Skipping...")
            continue

        ws_path = os.path.join(args.output_dir, ws_name)
        os.makedirs(ws_path, exist_ok=True)

        print(f"Workspace: {ws_name}")

        projects = get_projects(session, ws_guid)

        for proj in projects:

            proj_name = sanitize(proj["name"])
            
            proj_guid = proj.get("guid") or proj.get("id") or proj.get("project_id")
            
            if not proj_guid and "_links" in proj and "self" in proj["_links"]:
                href = proj["_links"]["self"]["href"]
                proj_guid = href.split("/")[-1]
            
            if not proj_guid:
                print(f"    ERROR: Could not find project GUID for '{proj_name}'. Skipping...")
                continue

            proj_path = os.path.join(ws_path, proj_name)
            os.makedirs(proj_path, exist_ok=True)

            print(f"  Project: {proj_name}")

            try:
                sbom = get_sbom(session, proj_guid, args.vulns, args.format)

                if sbom is None:
                    print("    No SBOM found (likely no recent agent scan)")
                    continue

                filename = f"sbom_{args.format}.json"
                with open(os.path.join(proj_path, filename), "w", encoding="utf-8") as f:
                    f.write(sbom)

                print("    SBOM saved")

            except Exception as e:

                with open(os.path.join(proj_path, "error.txt"), "w", encoding="utf-8") as f:
                    f.write(str(e))

                print(f"    Error: {e}")

if __name__ == "__main__":
    main()
