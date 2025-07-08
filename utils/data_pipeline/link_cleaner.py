import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FOLDER_PREFIX = os.getenv("S3_FOLDER_PREFIX")


def clean_s3_link(s3_link):
    """
    Cleans an S3-style link to a web-accessible URL.
    Example input: "s3://umass-unity-chatbot/documents/docs.unity.rc.umass.edu!documentation!cluster_specs_.md"
    Example output: "https://docs.unity.rc.umass.edu/documentation/cluster_specs"
    """
    s3_prefix = f"s3://{S3_BUCKET_NAME}/{S3_FOLDER_PREFIX}"
    web_protocol = "https://"
    file_extension = ".md"

    if not s3_link.startswith(s3_prefix):
        # If the link doesn't have the expected prefix, return it as is or raise an error
        return s3_link

    # 1. Remove the S3 prefix
    path_component = s3_link[len(s3_prefix) :]

    # 2. Handle the specific case of the .md extension
    # e.g., "something.md" should become "something" before replacing other underscores
    if path_component.endswith(f"{file_extension}"):
        # Remove the underscore and the extension
        # For "name.md", this becomes "name"
        path_component = path_component[: -(len(file_extension))]

    # 3. Replace all remaining underscores with slashes
    # For "docs.unity.rc.umass.edu!about.md", this becomes "docs.unity.rc.umass.edu/about"
    # For "docs.unity.rc.umass.edu_!documentation!cluster_specs.md", this becomes "docs.unity.rc.umass.edu/documentation/cluster_specs"
    cleaned_path = path_component.replace("!", "/")

    # 4. Prepend the web protocol
    return f"{web_protocol}{cleaned_path}"
