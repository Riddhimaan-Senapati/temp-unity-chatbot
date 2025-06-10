def clean_s3_link(s3_link):
    """
    Cleans an S3-style link to a web-accessible URL.
    Example input: "s3://umass-unity-chatbot/documents/docs.unity.rc.umass.edu_documentation_cluster_specs_.md"
    Example output: "https://docs.unity.rc.umass.edu/documentation/cluster_specs"
    """
    s3_prefix = "s3://umass-unity-chatbot/documents/"
    web_protocol = "https://"
    file_extension = ".md"

    if not s3_link.startswith(s3_prefix):
        # If the link doesn't have the expected prefix, return it as is or raise an error
        return s3_link

    # 1. Remove the S3 prefix
    path_component = s3_link[len(s3_prefix):]

    # 2. Handle the specific case of a trailing underscore and the .md extension
    # e.g., "something_.md" should become "something" before replacing other underscores
    if path_component.endswith(f"_{file_extension}"):
        # Remove the underscore and the extension
        # For "name_.md", this becomes "name"
        path_component = path_component[:- (len(file_extension) + 1)]
    
    # 3. Replace all remaining underscores with slashes
    # For "docs.unity.rc.umass.edu_about.md", this becomes "docs.unity.rc.umass.edu/about"
    # For "docs.unity.rc.umass.edu_documentation_cluster_specs.md", this becomes "docs.unity.rc.umass.edu/documentation/cluster/specs"
    cleaned_path = path_component.replace("_", "/")

    # 4. Prepend the web protocol
    return f"{web_protocol}{cleaned_path}"

"""
# Test cases based on real file names in our S3 bucket:
links_to_test = [
    "s3://umass-unity-chatbot/documents/docs.unity.rc.umass.edu_.md",
    "s3://umass-unity-chatbot/documents/docs.unity.rc.umass.edu_documentation_.md",
    "s3://umass-unity-chatbot/documents/docs.unity.rc.umass.edu_documentation_cluster_specs_.md",
    "s3://umass-unity-chatbot/documents/docs.unity.rc.umass.edu_about_.md",
]

print("Original -> Cleaned")
for link in links_to_test:
    print(f"{link} -> {clean_s3_link(link)}")

"""