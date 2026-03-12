import boomi_cicd


# Open release json
releases = boomi_cicd.set_release()

# Perform a query to get the branch id if needed.
# source_branch = boomi_cicd.get_branch_id("dev")
# destination_branch = boomi_cicd.get_branch_id("main")

# Optionally, create and execute a merge request before deployments.
# merge_request = boomi_cicd.create_merge_request(source_branch, destination_branch, "OVERRIDE", "SOURCE")
# boomi_cicd.execute_merge_request(merge_request, "MERGE")


environment_id = boomi_cicd.query_environment(boomi_cicd.ENVIRONMENT_NAME)

for release in releases["pipelines"]:
    component_id = release["componentId"]
    package_version = release["packageVersion"]
    notes = release.get("notes")

    package_id = boomi_cicd.query_packaged_component(component_id, package_version)

    if not package_id:
        package_id = boomi_cicd.create_packaged_component(
            component_id, package_version, notes
        )
        # Optionally, create the package from a specific branch. 
        # If the branch id is not provided, the default branch of the service account is used.
        # package_id = boomi_cicd.create_packaged_component(
        #     component_id, package_version, notes, destination_branch)

    # The third parameter determines if the package is currently deployed (True) or has every been deployed (False)
    package_deployed = boomi_cicd.query_deployed_package(
        package_id, environment_id, False
    )
    if not package_deployed:
        deployment_id = boomi_cicd.create_deployed_package(
            release, package_id, environment_id
        )
        # delete_deployed_package(deployment_id) # Delete deployment is useful for testing
