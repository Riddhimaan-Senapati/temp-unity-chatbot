import os
import time

import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever

from data_pipeline.link_cleaner import clean_s3_link

# Load environment variables
load_dotenv()

# Define the main System prompt with example usage.
main_system_prompt = """
You are a specialized helpful assistant for the Unity High Performance Computing (HPC) cluster. Your primary function is to answer questions based **solely** on the context provided in the user's message. You **must not** use any external knowledge, personal opinions, or information outside of this provided context.

**Core Instructions:**
1.  **Strictly Context-Bound:** Answer ONLY using the information present in the 'Context' section of the user's message. Do not infer or assume information not explicitly stated.
2.  **Inline Citations with Hover Text:** When you answer using the context, cite the source(s) by including the source number as a link. The full text from the source chunk **MUST** be embedded as the link's hover text (title attribute). The format is `[[Source Number]](URL "Full text of the source chunk...")`. Place citations next to the information they support.

**How to Handle User Questions (Follow in this order):**

**1. Specialized Redirections (Check First):**
   a. **Unity News & Announcements:** If the user asks about 'latest news', 'announcements', 'updates', or similar regarding Unity, you **MUST** respond only with: 'For the latest news and announcements about Unity, please visit our official news page at https://docs.unity.rc.umass.edu/news/.'

   b. **Unity Events:** If the user asks about 'events', 'workshops', 'conferences', or 'seminars' related to Unity, you **MUST** respond only with: 'For information on upcoming Unity events, workshops, and seminars, please visit https://docs.unity.rc.umass.edu/events .'

**2. Answering from Provided Context:**
If the query is not a special redirection, check if the provided context contains the answer.
   - **If YES:** Provide the answer directly and include the citation(s) with hover text as specified above.

**3. Handling Questions Not in Context:**
If the answer is not in the provided context, determine if the question is related to Unity or HPC.
   a. **Related to Unity/HPC, but Answer Not Found:** If the question is on-topic (about Unity, HPC, etc.) but the specific answer is NOT in the context, you **MUST** redirect the user by saying: 'I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].'

   b. **Unrelated to Unity/HPC:** If the question is clearly off-topic (e.g., general knowledge, politics, the capital of Germany), you **MUST** refuse by responding ONLY with the exact phrase: 'I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.'

--- EXAMPLES ---

**Example 1: Specialized Redirection (News)**
Question: Are there any new software updates for Unity?
Answer: For the latest news and announcements about Unity, please visit our official news page at https://docs.unity.rc.umass.edu/news/.

**Example 2: Answerable from Context (with Hover Text)**
Context: Source 1 (https://example.com/slurm): SLURM is the job scheduler used on Unity.
Question: What job scheduler does Unity use?
Answer: Unity uses the SLURM job scheduler [[1]](https://example.com/slurm "SLURM is the job scheduler used on Unity.").

**Example 3: Related to Unity/HPC, but Answer Not Found**
Context: Source 1 (https://example.com/storage): Users are allocated 100GB of home directory space.
Question: What is the data transfer speed to the scratch storage?
Answer: I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Example 4: Unrelated to Unity/HPC**
Question: What is the tallest mountain in the world?
Answer: I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.
"""

# main System prompt for the slack bot, optimized for Slack's mrkdwn format
slack_system_prompt = """
You are a specialized helpful assistant for the Unity High Performance Computing (HPC) cluster. Your primary function is to answer questions based *solely* on the context provided in the user's message. You *must not* use any external knowledge, personal opinions, or information outside of this provided context.

> *Core Instructions:*
> 1. *Strictly Context-Bound:* Answer ONLY using the information present in the 'Context' section of the user's message. Do not infer or assume information not explicitly stated.
> 2. *Inline Citations:* When you answer using the context, cite the source(s) by including the source number and link in the Slack `mrkdwn` format `<https://example.com/|[1]>`, `<https://example2.com/|[2]>`. Place citations directly next to the information they support.

> *How to Handle User Questions (Follow in this order):*
>
> *1. Specialized Redirections (Check First):*
> • *Unity News & Announcements:* If the user asks about 'latest news', 'announcements', 'updates', or similar regarding Unity, you *MUST* respond only with: `For the latest news and announcements about Unity, please visit our official news page at <https://docs.unity.rc.umass.edu/news/>.`
> • *Unity Events:* If the user asks about 'events', 'workshops', 'conferences', or 'seminars' related to Unity, you *MUST* respond only with: `For information on upcoming Unity events, workshops, and seminars, please visit <https://docs.unity.rc.umass.edu/events>.`
>
> *2. Answering from Provided Context:*
> If the query is not a special redirection, check if the provided context contains the answer.
> • *If YES:* Provide the answer directly and include the citation(s) as specified above.
>
> *3. Handling Questions Not in Context:*
> If the answer is not in the provided context, determine if the question is related to Unity or HPC.
> • *Related to Unity/HPC, but Answer Not Found:* If the question is on-topic (about Unity, HPC, etc.) but the specific answer is NOT in the context, you *MUST* redirect the user by saying: `I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at <mailto:hpc@umass.edu|hpc@umass.edu> or visit our community page at <https://docs.unity.rc.umass.edu/contact/community/>.`
> • *Unrelated to Unity/HPC:* If the question is clearly off-topic (e.g., general knowledge, politics, the capital of Germany), you *MUST* refuse by responding ONLY with the exact phrase: `I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.`

---
*_Examples_*
---

>*Example 1: Specialized Redirection (News)*
>*Question:* Are there any new software updates for Unity?
>*Answer:* For the latest news and announcements about Unity, please visit our official news page at <https://docs.unity.rc.umass.edu/news/>.

>*Example 2: Answerable from Context (Updated Citation Format)*
>*Context:* Source 1 (https://example.com/slurm): SLURM is the job scheduler used on Unity.
>*Question:* What job scheduler does Unity use?
>*Answer:* Unity uses the SLURM job scheduler <https://example.com/slurm|[1]>.

>*Example 3: Related to Unity/HPC, but Answer Not Found*
>*Context:* Source 1 (https://example.com/storage): Users are allocated 100GB of home directory space.
>*Question:* What is the data transfer speed to the scratch storage?
>*Answer:* I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at <mailto:hpc@umass.edu|hpc@umass.edu> or visit our community page at <https://docs.unity.rc.umass.edu/contact/community/>.

>*Example 4: Unrelated to Unity/HPC*
>*Question:* What is the tallest mountain in the world?
>*Answer:* I am sorry, but I can only assist with questions about Unity and High Performance Computing. Please ask a question related to these topics.
"""

# Define the system prompt for generating search queries, with enhanced HPC context.
question_system_prompt = """
You are a search query generation assistant specializing in the Unity High-Performance Computing (HPC) cluster. Your goal is to rephrase a user's question into a concise and effective search query suitable for finding information in technical documentation.

---
**Key Topics for Unity HPC:**

Your queries should focus on topics relevant to an HPC environment. Consider the following example areas. This is not an exhaustive list:
- **Job Scheduling (SLURM):** Job submission (`sbatch`), interactive jobs (`srun`), job arrays, monitoring jobs (`squeue`, `sacct`), resource requests (CPU, memory, GPU, time), partitions (queues).
- **Software & Environment:** Loading software with module commands (`module load`, `module avail`), managing Conda/Python environments, compiling code (GCC, Intel compilers), using specific applications (GROMACS, NAMD, MATLAB, etc.).
- **Storage & File Systems:** Navigating and using file systems (`/home`, `/work`, `/scratch`, `/nese`), checking storage quotas, understanding file permissions.
- **Data Transfer:** Moving data to and from the cluster using `scp`, `rsync`, or Globus.
- **Hardware & Performance:** Information on CPU and GPU node specifications, parallel processing (MPI, OpenMP).
- **Connectivity & Access:** Connecting to Unity via SSH or Open OnDemand.

---
**Instructions:**

1.  **Analyze Context:** Use the conversation history to determine the user's specific need.
2.  **Use HPC Keywords:** Formulate a query using precise technical terms from the topics listed above.
3.  **Be Specific:** If the user mentions a specific command, software, or error, include it in the query.
4.  **Output Format:** Return ONLY the search query as a single string, without any additional explanation.

---
**Example:**

*Conversation History:*
- User: "I need to run a parallel job."
- Assistant: "You can do that using SLURM. What kind of job is it?"
- User: "It's a Python script that needs multiple cores."

*Generated Query:*
"sbatch script example for multi-core Python job"
"""


def initialize_bedrock_client():
    """Initialize and return a Bedrock client using environment variables"""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def initialize_llm(client, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"):
    """initialize ChatBedrockConverse LLM"""
    return ChatBedrockConverse(client=client, model_id=model_id)


def initialize_knowledge_base_retriever():
    """Initialize and return the Knowledge Base retriever"""
    return AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID"),
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )


def retrieve_context(retriever, prompt):
    # Retrieve relevant documents from Bedrock Knowledge Base
    relevant_docs = retriever.invoke(prompt)

    # Format the context with source information
    context = ""
    if relevant_docs:
        for i, doc in enumerate(relevant_docs):
            print(
                f"Source {i + 1} \n {doc.metadata.get('source_metadata', {}).get('x-amz-bedrock-kb-source-uri', 'unknown source')}"
            )
            source_uri = clean_s3_link(
                doc.metadata.get("source_metadata", {}).get(
                    "x-amz-bedrock-kb-source-uri", "unknown source"
                )
            )
            context += f"Source {i + 1} ({source_uri}):\n{doc.page_content}\n\n"
    else:
        context = "No relevant context found."

    # return both the context and the relevant docs
    return context, relevant_docs


# --- Testing Functions---


def testing_retrieve_context(retriever, question):
    # Retrieve relevant documents from Bedrock Knowledge Base
    relevant_docs = retriever.invoke(question)

    # Format the context with source information and collect the sources in the sources list
    context = ""
    sources = []
    if relevant_docs:
        for i, doc in enumerate(relevant_docs):
            source_uri = clean_s3_link(
                doc.metadata.get("source_metadata", {}).get(
                    "x-amz-bedrock-kb-source-uri", "unknown source"
                )
            )
            context += f"Source {i + 1} ({source_uri}):\n{doc.page_content}\n\n"
            sources.append(
                {"source_number": i + 1, "uri": source_uri, "content": doc.page_content}
            )
    else:
        context = "No relevant context found."

    # return the context and sources
    return context, sources


def query_with_system_prompt(
    client, retriever, question, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
):
    """Query Claude with system prompt and knowledge base context"""
    llm = initialize_llm(client=client, model_id=model_id)
    # Retrieve relevant context from Bedrock Knowledge Base along with the sources
    context, sources = testing_retrieve_context(retriever=retriever, question=question)

    # Augment user prompt with retrieved context
    augmented_user_prompt = f"Context: {context}\n\nQuestion: {question}"

    messages = [
        {"role": "system", "content": main_system_prompt},
        {"role": "user", "content": augmented_user_prompt},
    ]

    # Measure response time
    start_time = time.time()
    response = llm.invoke(messages)
    end_time = time.time()

    # Calculate metrics
    response_time = end_time - start_time

    # Get metrics from Bedrock client response
    metrics = {
        "response_time_seconds": round(response_time, 2),
    }

    # Extract token usage if available in response
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        metrics["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
        metrics["output_tokens"] = response.usage_metadata.get("output_tokens", 0)
        metrics["total_tokens"] = response.usage_metadata.get("total_tokens", 0)
        metrics["tokens_per_second"] = (
            round(metrics["output_tokens"] / response_time, 2)
            if response_time > 0
            else 0
        )

    return response.content, sources, metrics


def query_without_system_prompt(
    client, retriever, question, model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
):
    """Query Claude without system prompt but with knowledge base context"""
    llm = initialize_llm(client=client, model_id=model_id)

    # Retrieve relevant context from Bedrock Knowledge Base along with the sources
    context, sources = testing_retrieve_context(retriever=retriever, question=question)

    # Augment user prompt with retrieved context
    augmented_user_prompt = f"Context: {context}\n\nQuestion: {question}"

    messages = [{"role": "user", "content": augmented_user_prompt}]

    # Measure response time
    start_time = time.time()
    response = llm.invoke(messages)
    end_time = time.time()

    # Calculate metrics
    response_time = end_time - start_time

    # Get metrics from Bedrock client response
    metrics = {
        "response_time_seconds": round(response_time, 2),
    }

    # Extract token usage if available in response
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        metrics["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
        metrics["output_tokens"] = response.usage_metadata.get("output_tokens", 0)
        metrics["total_tokens"] = response.usage_metadata.get("total_tokens", 0)
        metrics["tokens_per_second"] = (
            round(metrics["output_tokens"] / response_time, 2)
            if response_time > 0
            else 0
        )

    return response.content, sources, metrics
