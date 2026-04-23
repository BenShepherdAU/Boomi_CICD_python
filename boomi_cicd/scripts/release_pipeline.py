import boomi_cicd


# Open release json
releases = boomi_cicd.set_release()

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

    # The third parameter determines if the package is currently deployed (True) or has every been deployed (False)
    package_deployed = boomi_cicd.query_deployed_package(
        package_id, environment_id, False
    )
    if not package_deployed:
        deployment_id = boomi_cicd.create_deployed_package(
            release, package_id, environment_id
        )
        # delete_deployed_package(deployment_id) # Delete deployment is useful for testing
