import os


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    if os.environ.get("DEPLOY_ENVIRONMENT") == "staging":
        os.environ["TOOLCHEST_API_URL"] = os.environ["TOOLCHEST_STAGING_URL"]
