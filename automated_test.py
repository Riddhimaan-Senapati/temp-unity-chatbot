import os
import json
from dotenv import load_dotenv
from utils.chatbot_helper import (
    initialize_bedrock_client,
    initialize_knowledge_base_retriever,
    query_without_system_prompt,
    query_with_system_prompt,
    initialize_llm,
)

from utils.prompts import question_system_prompt

# Load environment variables
load_dotenv()

# Define available bedrock models
MODELS = {
    "claude-4-sonnet": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "claude-3.5-haiku": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "llama-4-maverick": "us.meta.llama4-maverick-17b-instruct-v1:0",
}

# Define pricing for each model (in $ per 1k tokens)
MODEL_PRICING = {
    "claude-4-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3.5-haiku": {"input": 0.0008, "output": 0.004},
    "llama-4-maverick": {"input": 0.00024, "output": 0.00097},
}


# Load conversation threads from JSON file
def load_conversation_threads(file_path="test_data/conversation_threads.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["threads"]


# Get a specific thread by name
def get_thread_by_name(threads, name):
    for thread in threads:
        if thread["name"].lower() == name.lower():
            return thread
    return None


# Calculate the cost of a query based on model and token usage
def calculate_query_cost(model_name, input_tokens, output_tokens):
    if model_name not in MODEL_PRICING:
        return {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0}

    pricing = MODEL_PRICING[model_name]
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
    }


# Runs the chosen model on the full database of conversation threads
def test_model_on_database(model_name):
    # Initialize clients
    client = initialize_bedrock_client()
    retriever = initialize_knowledge_base_retriever()

    # Get model ID
    model_id = MODELS.get(model_name)
    if not model_id:
        print(f"Model '{model_name}' not found")
        list_models()
        return None

    # Load all threads
    all_threads = load_conversation_threads()

    # Initialize results structure
    results = {
        "model_name": model_name,
        "model_id": model_id,
        "test_timestamp": "",
        "threads": {},
        "summary_metrics": {
            "total_queries": 0,
            "total_response_time": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0,
            "average_response_time": 0,
            "average_tokens_per_second": 0,
            "threads_processed": 0,
        },
    }

    print(f"Testing model: {model_name}")
    print(f"Processing {len(all_threads)} conversation threads...")

    # Process each thread
    for thread_idx, thread in enumerate(all_threads):
        thread_name = thread["name"]
        print(f"\nProcessing thread {thread_idx + 1}/{len(all_threads)}: {thread_name}")

        # Initialize thread results
        results["threads"][thread_name] = {
            "messages": [],
            "thread_metrics": {
                "total_queries": len(thread["messages"]),
                "total_response_time": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0,
                "average_response_time": 0,
                "average_tokens_per_second": 0,
            },
        }

        # Process each message in the thread
        conversation_context = []

        for msg_idx, question in enumerate(thread["messages"]):
            print(
                f"  Question {msg_idx + 1}/{len(thread['messages'])}: {question[:25]}..."
            )

            # Generate optimized search query using conversation history (duplicate from chatbot.py)
            llm = initialize_llm(client=client, model_id=model_id)
            optimized_query = question  # Fallback

            if conversation_context:
                # Build query messages with conversation history
                query_messages = [
                    {"role": "system", "content": question_system_prompt},
                    *[
                        {
                            "role": "user" if i % 2 == 0 else "assistant",
                            "content": ctx["question"] if i % 2 == 0 else ctx["answer"],
                        }
                        for i, ctx in enumerate(
                            conversation_context[-3:]
                        )  # Last 3 Q&A pairs
                        for _ in [0, 1]  # Create both user and assistant messages
                    ][:-1],  # Remove last assistant message to end with user
                    {
                        "role": "user",
                        "content": f"Based on this conversation history, generate a search query for: {question}",
                    },
                ]

                try:
                    # Get optimized query from secondary LLM
                    query_response = llm.invoke(query_messages)
                    optimized_query_content = (
                        query_response.content.strip()
                        if hasattr(query_response, "content")
                        else str(query_response).strip()
                    )
                    if optimized_query_content:
                        optimized_query = optimized_query_content
                except Exception:
                    pass  # Fall back to original question

            # Query with system prompt using optimized query
            response, sources, metrics = query_with_system_prompt(
                client, retriever, optimized_query, model_id
            )

            # Calculate cost
            cost_info = calculate_query_cost(
                model_name,
                metrics.get("input_tokens", 0),
                metrics.get("output_tokens", 0),
            )

            # Add cost to metrics
            metrics.update(cost_info)

            # Store in conversation context
            conversation_context.append({"question": question, "answer": response})

            # Store message result
            message_result = {
                "question_number": msg_idx + 1,
                "question": question,
                "answer": response,
                "sources": sources,
                "metrics": metrics,
            }

            results["threads"][thread_name]["messages"].append(message_result)

            # Update thread metrics
            thread_metrics = results["threads"][thread_name]["thread_metrics"]
            thread_metrics["total_response_time"] += metrics.get(
                "response_time_seconds", 0
            )
            thread_metrics["total_input_tokens"] += metrics.get("input_tokens", 0)
            thread_metrics["total_output_tokens"] += metrics.get("output_tokens", 0)
            thread_metrics["total_cost"] += metrics.get("total_cost", 0)

            # Update global metrics
            summary = results["summary_metrics"]
            summary["total_queries"] += 1
            summary["total_response_time"] += metrics.get("response_time_seconds", 0)
            summary["total_input_tokens"] += metrics.get("input_tokens", 0)
            summary["total_output_tokens"] += metrics.get("output_tokens", 0)
            summary["total_cost"] += metrics.get("total_cost", 0)

        # Calculate thread averages
        thread_metrics = results["threads"][thread_name]["thread_metrics"]
        if thread_metrics["total_queries"] > 0:
            thread_metrics["average_response_time"] = round(
                thread_metrics["total_response_time"] / thread_metrics["total_queries"],
                3,
            )
            if thread_metrics["total_response_time"] > 0:
                total_tokens = (
                    thread_metrics["total_input_tokens"]
                    + thread_metrics["total_output_tokens"]
                )
                thread_metrics["average_tokens_per_second"] = round(
                    total_tokens / thread_metrics["total_response_time"], 2
                )

        results["summary_metrics"]["threads_processed"] += 1

    # Calculate global averages
    summary = results["summary_metrics"]
    if summary["total_queries"] > 0:
        summary["average_response_time"] = round(
            summary["total_response_time"] / summary["total_queries"], 3
        )
        if summary["total_response_time"] > 0:
            total_tokens = (
                summary["total_input_tokens"] + summary["total_output_tokens"]
            )
            summary["average_tokens_per_second"] = round(
                total_tokens / summary["total_response_time"], 2
            )

    # Round cost values
    summary["total_cost"] = round(summary["total_cost"], 6)

    # Create test_results directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), "test_results")
    os.makedirs(results_dir, exist_ok=True)

    # Create filename based on model name
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_database_test_{model_name}_{timestamp}"

    # Update timestamp in results
    results["test_timestamp"] = timestamp

    # Save results to JSON file
    json_file = os.path.join(results_dir, f"{filename}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {json_file}")

    # Convert JSON to Markdown
    md_file = database_json_to_markdown(json_file)
    print(f"Markdown report generated at {md_file}")

    # Print summary
    print("\n=== TEST SUMMARY ===")
    print(f"Model: {model_name}")
    print(f"Total queries: {summary['total_queries']}")
    print(f"Total cost: ${summary['total_cost']}")
    print(f"Average response time: {summary['average_response_time']} seconds")
    print(f"Average tokens/second: {summary['average_tokens_per_second']}")

    return json_file


def database_json_to_markdown(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    markdown = f"# Full Database Test Results - {results['model_name']}\n\n"
    markdown += f"**Test Timestamp:** {results['test_timestamp']}\n\n"
    markdown += f"**Model ID:** `{results['model_id']}`\n\n"

    # Summary metrics at the top
    summary = results["summary_metrics"]
    markdown += "## Summary Metrics\n\n"
    markdown += f"- **Total Queries:** {summary['total_queries']}\n"
    markdown += f"- **Threads Processed:** {summary['threads_processed']}\n"
    markdown += (
        f"- **Total Response Time:** {summary['total_response_time']:.3f} seconds\n"
    )
    markdown += (
        f"- **Average Response Time:** {summary['average_response_time']:.3f} seconds\n"
    )
    markdown += f"- **Total Input Tokens:** {summary['total_input_tokens']:,}\n"
    markdown += f"- **Total Output Tokens:** {summary['total_output_tokens']:,}\n"
    markdown += f"- **Total Tokens:** {summary['total_input_tokens'] + summary['total_output_tokens']:,}\n"
    markdown += (
        f"- **Average Tokens/Second:** {summary['average_tokens_per_second']:.2f}\n"
    )
    markdown += f"- **Total Cost:** ${summary['total_cost']:.6f}\n\n"

    markdown += "---\n\n"

    # Detailed responses by thread in order
    markdown += "## Detailed Responses by Thread\n\n"

    for thread_name, thread_data in results["threads"].items():
        markdown += f"### Thread: {thread_name}\n\n"

        # Thread summary
        thread_metrics = thread_data["thread_metrics"]
        markdown += "**Thread Summary:**\n"
        markdown += f"- Queries: {thread_metrics['total_queries']}\n"
        markdown += f"- Total Response Time: {thread_metrics['total_response_time']:.3f} seconds\n"
        markdown += f"- Average Response Time: {thread_metrics['average_response_time']:.3f} seconds\n"
        markdown += f"- Total Cost: ${thread_metrics['total_cost']:.6f}\n"
        markdown += f"- Average Tokens/Second: {thread_metrics['average_tokens_per_second']:.2f}\n\n"

        # Individual messages with responses and metrics
        for message in thread_data["messages"]:
            markdown += f"#### Q{message['question_number']}: {message['question']}\n\n"
            markdown += f"**Response:**\n\n{message['answer']}\n\n"

            # Individual query metrics
            metrics = message["metrics"]
            markdown += "**Query Metrics:**\n"
            markdown += f"- Response Time: {metrics.get('response_time_seconds', 'N/A'):.3f} seconds\n"
            markdown += f"- Input Tokens: {metrics.get('input_tokens', 'N/A'):,}\n"
            markdown += f"- Output Tokens: {metrics.get('output_tokens', 'N/A'):,}\n"
            markdown += f"- Total Tokens: {metrics.get('total_tokens', 'N/A'):,}\n"
            markdown += (
                f"- Tokens/Second: {metrics.get('tokens_per_second', 'N/A'):.2f}\n"
            )
            markdown += f"- Input Cost: ${metrics.get('input_cost', 'N/A'):.6f}\n"
            markdown += f"- Output Cost: ${metrics.get('output_cost', 'N/A'):.6f}\n"
            markdown += f"- Total Cost: ${metrics.get('total_cost', 'N/A'):.6f}\n\n"

            # Sources
            if message["sources"]:
                markdown += f"**Sources ({len(message['sources'])}):**\n"
                for source in message["sources"]:
                    markdown += f"- [{source['uri']}]({source['uri']})\n"
                markdown += "\n"

            markdown += "---\n\n"

    # Write markdown to file
    md_file = json_file.replace(".json", ".md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    return md_file


# List available models if requested
def list_models():
    print("Available models:")
    for model_name in MODELS.keys():
        print(f"- {model_name}")
    return


# List available threads if requested
def list_threads():
    all_threads = load_conversation_threads()
    print("Available conversation threads:")
    for i, thread in enumerate(all_threads):
        print(f"{i}: {thread['name']}")
    return


### Function to run the chosen thread with all models
def compare_models(thread_name):
    # Initialize clients
    client = initialize_bedrock_client()
    retriever = initialize_knowledge_base_retriever()

    # Load all threads
    all_threads = load_conversation_threads()

    # Find the requested thread
    thread = get_thread_by_name(all_threads, thread_name)
    if not thread:
        print(f"Thread '{thread_name}' not found")
        list_threads()
        return None

    # Initialize results structure
    results = {
        "thread_name": thread_name,
        "test_timestamp": "",
        "models": {},
        "summary_metrics": {
            "total_models_tested": 0,
            "total_queries_per_model": len(thread["messages"]),
            "total_queries_all_models": 0,
            "best_performance": {
                "fastest_model": "",
                "fastest_avg_time": float("inf"),
                "cheapest_model": "",
                "lowest_cost": float("inf"),
                "most_tokens_per_second": "",
                "highest_tokens_per_second": 0,
            },
        },
    }

    print(f"Testing all models on thread: {thread_name}")
    print(
        f"Processing {len(MODELS)} models with {len(thread['messages'])} questions each..."
    )

    # Process each model
    for model_idx, (model_name, model_id) in enumerate(MODELS.items()):
        print(f"\nTesting model {model_idx + 1}/{len(MODELS)}: {model_name}")

        # Initialize model results
        results["models"][model_name] = {
            "model_id": model_id,
            "messages": [],
            "model_metrics": {
                "total_queries": len(thread["messages"]),
                "total_response_time": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0,
                "average_response_time": 0,
                "average_tokens_per_second": 0,
            },
        }

        # Process each message in the thread for this model
        for msg_idx, question in enumerate(thread["messages"]):
            print(
                f"  Question {msg_idx + 1}/{len(thread['messages'])}: {question[:50]}..."
            )

            try:
                # Query with system prompt
                response, sources, metrics = query_with_system_prompt(
                    client, retriever, question, model_id
                )

                # Calculate cost
                cost_info = calculate_query_cost(
                    model_name,
                    metrics.get("input_tokens", 0),
                    metrics.get("output_tokens", 0),
                )

                # Add cost to metrics
                metrics.update(cost_info)

                # Store message result
                message_result = {
                    "question_number": msg_idx + 1,
                    "question": question,
                    "answer": response,
                    "sources": sources,
                    "metrics": metrics,
                }

                results["models"][model_name]["messages"].append(message_result)

                # Update model metrics
                model_metrics = results["models"][model_name]["model_metrics"]
                model_metrics["total_response_time"] += metrics.get(
                    "response_time_seconds", 0
                )
                model_metrics["total_input_tokens"] += metrics.get("input_tokens", 0)
                model_metrics["total_output_tokens"] += metrics.get("output_tokens", 0)
                model_metrics["total_cost"] += metrics.get("total_cost", 0)

            except Exception as e:
                print(f"    Error processing question with {model_name}: {str(e)}")
                # Add error message
                error_result = {
                    "question_number": msg_idx + 1,
                    "question": question,
                    "answer": f"ERROR: {str(e)}",
                    "sources": [],
                    "metrics": {
                        "response_time_seconds": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "tokens_per_second": 0,
                        "input_cost": 0,
                        "output_cost": 0,
                        "total_cost": 0,
                    },
                }
                results["models"][model_name]["messages"].append(error_result)

        # Calculate model averages
        model_metrics = results["models"][model_name]["model_metrics"]
        if model_metrics["total_queries"] > 0:
            model_metrics["average_response_time"] = round(
                model_metrics["total_response_time"] / model_metrics["total_queries"], 3
            )
            if model_metrics["total_response_time"] > 0:
                total_tokens = (
                    model_metrics["total_input_tokens"]
                    + model_metrics["total_output_tokens"]
                )
                model_metrics["average_tokens_per_second"] = round(
                    total_tokens / model_metrics["total_response_time"], 2
                )

        # Update summary metrics
        results["summary_metrics"]["total_models_tested"] += 1
        results["summary_metrics"]["total_queries_all_models"] += model_metrics[
            "total_queries"
        ]

        # Update best performance tracking
        best_perf = results["summary_metrics"]["best_performance"]

        # Fastest model
        if (
            model_metrics["average_response_time"] > 0
            and model_metrics["average_response_time"] < best_perf["fastest_avg_time"]
        ):
            best_perf["fastest_model"] = model_name
            best_perf["fastest_avg_time"] = model_metrics["average_response_time"]

        # Cheapest model
        if model_metrics["total_cost"] < best_perf["lowest_cost"]:
            best_perf["cheapest_model"] = model_name
            best_perf["lowest_cost"] = model_metrics["total_cost"]

        # Most tokens per second
        if (
            model_metrics["average_tokens_per_second"]
            > best_perf["highest_tokens_per_second"]
        ):
            best_perf["most_tokens_per_second"] = model_name
            best_perf["highest_tokens_per_second"] = model_metrics[
                "average_tokens_per_second"
            ]

    # Create test_results directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), "test_results")
    os.makedirs(results_dir, exist_ok=True)

    # Create filename based on thread name
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"compare_models_{thread_name.replace(' ', '_')}_{timestamp}"

    # Update timestamp in results
    results["test_timestamp"] = timestamp

    # Save results to JSON file
    json_file = os.path.join(results_dir, f"{filename}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {json_file}")

    # Convert JSON to Markdown
    md_file = compare_models_json_to_markdown(json_file)
    print(f"Markdown report generated at {md_file}")

    # Print summary
    print("\n=== MODEL COMPARISON SUMMARY ===")
    print(f"Thread: {thread_name}")
    print(f"Models tested: {results['summary_metrics']['total_models_tested']}")
    print(
        f"Questions per model: {results['summary_metrics']['total_queries_per_model']}"
    )
    print(
        f"Fastest model: {best_perf['fastest_model']} ({best_perf['fastest_avg_time']:.3f}s avg)"
    )
    print(
        f"Cheapest model: {best_perf['cheapest_model']} (${best_perf['lowest_cost']:.6f})"
    )
    print(
        f"Highest tokens/sec: {best_perf['most_tokens_per_second']} ({best_perf['highest_tokens_per_second']:.2f})"
    )

    return json_file


def compare_models_json_to_markdown(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    markdown = f"# Model Comparison Results - {results['thread_name']}\n\n"
    markdown += f"**Test Timestamp:** {results['test_timestamp']}\n\n"

    # Summary metrics at the top
    summary = results["summary_metrics"]
    best_perf = summary["best_performance"]

    markdown += "## Summary Metrics\n\n"
    markdown += f"- **Thread Tested:** {results['thread_name']}\n"
    markdown += f"- **Models Tested:** {summary['total_models_tested']}\n"
    markdown += f"- **Questions per Model:** {summary['total_queries_per_model']}\n"
    markdown += (
        f"- **Total Queries (All Models):** {summary['total_queries_all_models']}\n\n"
    )

    markdown += "### Best Performance\n\n"
    markdown += f"- **Fastest Model:** {best_perf['fastest_model']} ({best_perf['fastest_avg_time']:.3f}s avg)\n"
    markdown += f"- **Cheapest Model:** {best_perf['cheapest_model']} (${best_perf['lowest_cost']:.6f} total)\n"
    markdown += f"- **Highest Tokens/Second:** {best_perf['most_tokens_per_second']} ({best_perf['highest_tokens_per_second']:.2f})\n\n"

    # Model comparison table
    markdown += "## Model Performance Comparison\n\n"
    markdown += "| Model | Avg Response Time (s) | Total Cost ($) | Avg Tokens/Sec | Total Input Tokens | Total Output Tokens |\n"
    markdown += "|-------|----------------------|----------------|----------------|-------------------|--------------------|\n"

    for model_name, model_data in results["models"].items():
        metrics = model_data["model_metrics"]
        markdown += f"| {model_name} | {metrics['average_response_time']:.3f} | ${metrics['total_cost']:.6f} | {metrics['average_tokens_per_second']:.2f} | {metrics['total_input_tokens']:,} | {metrics['total_output_tokens']:,} |\n"

    markdown += "\n---\n\n"

    # Detailed responses by model
    markdown += "## Detailed Responses by Model\n\n"

    for model_name, model_data in results["models"].items():
        markdown += f"### Model: {model_name}\n\n"
        markdown += f"**Model ID:** `{model_data['model_id']}`\n\n"

        # Model summary
        model_metrics = model_data["model_metrics"]
        markdown += "**Model Summary:**\n"
        markdown += f"- Queries: {model_metrics['total_queries']}\n"
        markdown += f"- Total Response Time: {model_metrics['total_response_time']:.3f} seconds\n"
        markdown += f"- Average Response Time: {model_metrics['average_response_time']:.3f} seconds\n"
        markdown += f"- Total Cost: ${model_metrics['total_cost']:.6f}\n"
        markdown += f"- Average Tokens/Second: {model_metrics['average_tokens_per_second']:.2f}\n"
        markdown += f"- Total Input Tokens: {model_metrics['total_input_tokens']:,}\n"
        markdown += (
            f"- Total Output Tokens: {model_metrics['total_output_tokens']:,}\n\n"
        )

        # Individual messages with responses and metrics
        for message in model_data["messages"]:
            markdown += f"#### Q{message['question_number']}: {message['question']}\n\n"
            markdown += f"**Response:**\n\n{message['answer']}\n\n"

            # Individual query metrics
            metrics = message["metrics"]
            markdown += "**Query Metrics:**\n"
            markdown += f"- Response Time: {metrics.get('response_time_seconds', 'N/A'):.3f} seconds\n"
            markdown += f"- Input Tokens: {metrics.get('input_tokens', 'N/A'):,}\n"
            markdown += f"- Output Tokens: {metrics.get('output_tokens', 'N/A'):,}\n"
            markdown += f"- Total Tokens: {metrics.get('total_tokens', 'N/A'):,}\n"
            markdown += (
                f"- Tokens/Second: {metrics.get('tokens_per_second', 'N/A'):.2f}\n"
            )
            markdown += f"- Input Cost: ${metrics.get('input_cost', 'N/A'):.6f}\n"
            markdown += f"- Output Cost: ${metrics.get('output_cost', 'N/A'):.6f}\n"
            markdown += f"- Total Cost: ${metrics.get('total_cost', 'N/A'):.6f}\n\n"

            # Sources
            if message["sources"]:
                markdown += f"**Sources ({len(message['sources'])}):**\n"
                for source in message["sources"]:
                    markdown += f"- [{source['uri']}]({source['uri']})\n"
                markdown += "\n"

            markdown += "---\n\n"

        markdown += "\n"

    # Write markdown to file
    md_file = json_file.replace(".json", ".md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    return md_file


def test_model_with_without_system_prompt(model_name, thread_name):
    """Test a specific model with and without system prompt on a chosen thread with comprehensive metrics"""

    # Initialize clients
    client = initialize_bedrock_client()
    retriever = initialize_knowledge_base_retriever()

    # Get model ID
    model_id = MODELS.get(model_name)
    if not model_id:
        print(f"Model '{model_name}' not found")
        list_models()
        return None

    # Load all threads
    all_threads = load_conversation_threads()

    # Find the requested thread
    thread = get_thread_by_name(all_threads, thread_name)
    if not thread:
        print(f"Thread '{thread_name}' not found")
        list_threads()
        return None

    # Initialize results structure
    results = {
        "model_name": model_name,
        "model_id": model_id,
        "thread_name": thread_name,
        "test_timestamp": "",
        "configurations": {
            "with_system_prompt": {
                "messages": [],
                "metrics": {
                    "total_queries": len(thread["messages"]),
                    "total_response_time": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_cost": 0,
                    "average_response_time": 0,
                    "average_tokens_per_second": 0,
                },
            },
            "without_system_prompt": {
                "messages": [],
                "metrics": {
                    "total_queries": len(thread["messages"]),
                    "total_response_time": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_cost": 0,
                    "average_response_time": 0,
                    "average_tokens_per_second": 0,
                },
            },
        },
        "comparison_metrics": {
            "response_time_difference": 0,
            "cost_difference": 0,
            "tokens_per_second_difference": 0,
            "faster_configuration": "",
            "cheaper_configuration": "",
            "more_efficient_configuration": "",
        },
    }

    print(f"Testing model: {model_name} on thread: {thread_name}")
    print("Testing both WITH and WITHOUT system prompt")
    print(f"Processing {len(thread['messages'])} questions...")

    # Process each message in the thread for both configurations
    for msg_idx, question in enumerate(thread["messages"]):
        print(f"\nQuestion {msg_idx + 1}/{len(thread['messages'])}: {question[:50]}...")

        # Test WITH system prompt
        print("  Testing with system prompt...")
        try:
            response_with, sources_with, metrics_with = query_with_system_prompt(
                client, retriever, question, model_id
            )

            # Calculate cost for with system prompt
            cost_info_with = calculate_query_cost(
                model_name,
                metrics_with.get("input_tokens", 0),
                metrics_with.get("output_tokens", 0),
            )
            metrics_with.update(cost_info_with)

            # Store message result for with system prompt
            message_result_with = {
                "question_number": msg_idx + 1,
                "question": question,
                "answer": response_with,
                "sources": sources_with,
                "metrics": metrics_with,
            }

            results["configurations"]["with_system_prompt"]["messages"].append(
                message_result_with
            )

            # Update metrics for with system prompt
            with_metrics = results["configurations"]["with_system_prompt"]["metrics"]
            with_metrics["total_response_time"] += metrics_with.get(
                "response_time_seconds", 0
            )
            with_metrics["total_input_tokens"] += metrics_with.get("input_tokens", 0)
            with_metrics["total_output_tokens"] += metrics_with.get("output_tokens", 0)
            with_metrics["total_cost"] += metrics_with.get("total_cost", 0)

        except Exception as e:
            print(f"    Error with system prompt: {str(e)}")
            error_result_with = {
                "question_number": msg_idx + 1,
                "question": question,
                "answer": f"ERROR: {str(e)}",
                "sources": [],
                "metrics": {
                    "response_time_seconds": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "tokens_per_second": 0,
                    "input_cost": 0,
                    "output_cost": 0,
                    "total_cost": 0,
                },
            }
            results["configurations"]["with_system_prompt"]["messages"].append(
                error_result_with
            )

        # Test WITHOUT system prompt
        print("  Testing without system prompt...")
        try:
            response_without, sources_without, metrics_without = (
                query_without_system_prompt(client, retriever, question, model_id)
            )

            # Calculate cost for without system prompt
            cost_info_without = calculate_query_cost(
                model_name,
                metrics_without.get("input_tokens", 0),
                metrics_without.get("output_tokens", 0),
            )
            metrics_without.update(cost_info_without)

            # Store message result for without system prompt
            message_result_without = {
                "question_number": msg_idx + 1,
                "question": question,
                "answer": response_without,
                "sources": sources_without,
                "metrics": metrics_without,
            }

            results["configurations"]["without_system_prompt"]["messages"].append(
                message_result_without
            )

            # Update metrics for without system prompt
            without_metrics = results["configurations"]["without_system_prompt"][
                "metrics"
            ]
            without_metrics["total_response_time"] += metrics_without.get(
                "response_time_seconds", 0
            )
            without_metrics["total_input_tokens"] += metrics_without.get(
                "input_tokens", 0
            )
            without_metrics["total_output_tokens"] += metrics_without.get(
                "output_tokens", 0
            )
            without_metrics["total_cost"] += metrics_without.get("total_cost", 0)

        except Exception as e:
            print(f"    Error without system prompt: {str(e)}")
            error_result_without = {
                "question_number": msg_idx + 1,
                "question": question,
                "answer": f"ERROR: {str(e)}",
                "sources": [],
                "metrics": {
                    "response_time_seconds": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "tokens_per_second": 0,
                    "input_cost": 0,
                    "output_cost": 0,
                    "total_cost": 0,
                },
            }
            results["configurations"]["without_system_prompt"]["messages"].append(
                error_result_without
            )

    # Calculate averages for both configurations
    for config_name, config_data in results["configurations"].items():
        config_metrics = config_data["metrics"]
        if config_metrics["total_queries"] > 0:
            config_metrics["average_response_time"] = round(
                config_metrics["total_response_time"] / config_metrics["total_queries"],
                3,
            )
            if config_metrics["total_response_time"] > 0:
                total_tokens = (
                    config_metrics["total_input_tokens"]
                    + config_metrics["total_output_tokens"]
                )
                config_metrics["average_tokens_per_second"] = round(
                    total_tokens / config_metrics["total_response_time"], 2
                )

    # Calculate comparison metrics
    with_metrics = results["configurations"]["with_system_prompt"]["metrics"]
    without_metrics = results["configurations"]["without_system_prompt"]["metrics"]
    comparison = results["comparison_metrics"]

    comparison["response_time_difference"] = round(
        with_metrics["average_response_time"]
        - without_metrics["average_response_time"],
        3,
    )
    comparison["cost_difference"] = round(
        with_metrics["total_cost"] - without_metrics["total_cost"], 6
    )
    comparison["tokens_per_second_difference"] = round(
        with_metrics["average_tokens_per_second"]
        - without_metrics["average_tokens_per_second"],
        2,
    )

    # Determine which configuration is better
    comparison["faster_configuration"] = (
        "with_system_prompt"
        if with_metrics["average_response_time"]
        < without_metrics["average_response_time"]
        else "without_system_prompt"
    )
    comparison["cheaper_configuration"] = (
        "with_system_prompt"
        if with_metrics["total_cost"] < without_metrics["total_cost"]
        else "without_system_prompt"
    )
    comparison["more_efficient_configuration"] = (
        "with_system_prompt"
        if with_metrics["average_tokens_per_second"]
        > without_metrics["average_tokens_per_second"]
        else "without_system_prompt"
    )

    # Create test_results directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), "test_results")
    os.makedirs(results_dir, exist_ok=True)

    # Create filename
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"system_prompt_comparison_{model_name}_{thread_name.replace(' ', '_')}_{timestamp}"

    # Update timestamp in results
    results["test_timestamp"] = timestamp

    # Save results to JSON file
    json_file = os.path.join(results_dir, f"{filename}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {json_file}")

    # Convert JSON to Markdown
    md_file = system_prompt_comparison_json_to_markdown(json_file)
    print(f"Markdown report generated at {md_file}")

    # Print summary
    print("\n=== SYSTEM PROMPT COMPARISON SUMMARY ===")
    print(f"Model: {model_name}")
    print(f"Thread: {thread_name}")
    print(
        f"Faster configuration: {comparison['faster_configuration']} (difference: {comparison['response_time_difference']:.3f}s)"
    )
    print(
        f"Cheaper configuration: {comparison['cheaper_configuration']} (difference: ${comparison['cost_difference']:.6f})"
    )
    print(
        f"More efficient configuration: {comparison['more_efficient_configuration']} (difference: {comparison['tokens_per_second_difference']:.2f} tokens/s)"
    )

    return json_file


def system_prompt_comparison_json_to_markdown(json_file):
    """Convert system prompt comparison JSON results to readable Markdown format"""
    with open(json_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    markdown = f"# System Prompt Comparison - {results['model_name']} on {results['thread_name']}\n\n"
    markdown += f"**Test Timestamp:** {results['test_timestamp']}\n\n"
    markdown += f"**Model:** {results['model_name']}\n\n"
    markdown += f"**Model ID:** `{results['model_id']}`\n\n"
    markdown += f"**Thread:** {results['thread_name']}\n\n"

    # Summary metrics at the top
    with_metrics = results["configurations"]["with_system_prompt"]["metrics"]
    without_metrics = results["configurations"]["without_system_prompt"]["metrics"]
    comparison = results["comparison_metrics"]

    markdown += "## Summary Metrics\n\n"

    # Comparison table
    markdown += "### Performance Comparison\n\n"
    markdown += "| Configuration | Avg Response Time (s) | Total Cost ($) | Avg Tokens/Sec | Total Input Tokens | Total Output Tokens |\n"
    markdown += "|---------------|----------------------|----------------|----------------|-------------------|--------------------|\n"
    markdown += f"| With System Prompt | {with_metrics['average_response_time']:.3f} | ${with_metrics['total_cost']:.6f} | {with_metrics['average_tokens_per_second']:.2f} | {with_metrics['total_input_tokens']:,} | {with_metrics['total_output_tokens']:,} |\n"
    markdown += f"| Without System Prompt | {without_metrics['average_response_time']:.3f} | ${without_metrics['total_cost']:.6f} | {without_metrics['average_tokens_per_second']:.2f} | {without_metrics['total_input_tokens']:,} | {without_metrics['total_output_tokens']:,} |\n"
    markdown += f"| **Difference** | **{comparison['response_time_difference']:+.3f}** | **${comparison['cost_difference']:+.6f}** | **{comparison['tokens_per_second_difference']:+.2f}** | **{with_metrics['total_input_tokens'] - without_metrics['total_input_tokens']:+,}** | **{with_metrics['total_output_tokens'] - without_metrics['total_output_tokens']:+,}** |\n\n"

    markdown += "### Winner Summary\n\n"
    markdown += f"- **Faster Configuration:** {comparison['faster_configuration'].replace('_', ' ').title()}\n"
    markdown += f"- **Cheaper Configuration:** {comparison['cheaper_configuration'].replace('_', ' ').title()}\n"
    markdown += f"- **More Efficient Configuration:** {comparison['more_efficient_configuration'].replace('_', ' ').title()}\n\n"

    markdown += "---\n\n"

    # Detailed responses by configuration
    markdown += "## Detailed Responses by Configuration\n\n"

    for config_name, config_data in results["configurations"].items():
        config_title = config_name.replace("_", " ").title()
        markdown += f"### {config_title}\n\n"

        # Configuration summary
        config_metrics = config_data["metrics"]
        markdown += "**Configuration Summary:**\n"
        markdown += f"- Queries: {config_metrics['total_queries']}\n"
        markdown += f"- Total Response Time: {config_metrics['total_response_time']:.3f} seconds\n"
        markdown += f"- Average Response Time: {config_metrics['average_response_time']:.3f} seconds\n"
        markdown += f"- Total Cost: ${config_metrics['total_cost']:.6f}\n"
        markdown += f"- Average Tokens/Second: {config_metrics['average_tokens_per_second']:.2f}\n"
        markdown += f"- Total Input Tokens: {config_metrics['total_input_tokens']:,}\n"
        markdown += (
            f"- Total Output Tokens: {config_metrics['total_output_tokens']:,}\n\n"
        )

        # Individual messages with responses and metrics
        for message in config_data["messages"]:
            markdown += f"#### Q{message['question_number']}: {message['question']}\n\n"
            markdown += f"**Response:**\n\n{message['answer']}\n\n"

            # Individual query metrics
            metrics = message["metrics"]
            markdown += "**Query Metrics:**\n"
            markdown += f"- Response Time: {metrics.get('response_time_seconds', 'N/A'):.3f} seconds\n"
            markdown += f"- Input Tokens: {metrics.get('input_tokens', 'N/A'):,}\n"
            markdown += f"- Output Tokens: {metrics.get('output_tokens', 'N/A'):,}\n"
            markdown += f"- Total Tokens: {metrics.get('total_tokens', 'N/A'):,}\n"
            markdown += (
                f"- Tokens/Second: {metrics.get('tokens_per_second', 'N/A'):.2f}\n"
            )
            markdown += f"- Input Cost: ${metrics.get('input_cost', 'N/A'):.6f}\n"
            markdown += f"- Output Cost: ${metrics.get('output_cost', 'N/A'):.6f}\n"
            markdown += f"- Total Cost: ${metrics.get('total_cost', 'N/A'):.6f}\n\n"

            # Sources
            if message["sources"]:
                markdown += f"**Sources ({len(message['sources'])}):**\n"
                for source in message["sources"]:
                    markdown += f"- [{source['uri']}]({source['uri']})\n"
                markdown += "\n"

            markdown += "---\n\n"

        markdown += "\n"

    # Write markdown to file
    md_file = json_file.replace(".json", ".md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    return md_file


# Example usage:
### Use list_models() to see available models
### Use list_threads() to see available conversation threads
### Use test_model_on_database(model_name) to test a single model on all threads
### Use compare_models(thread_name) to test all models on a single thread
### Use test_model_with_without_system_prompt(model_name, thread_name) to test one model with/without system prompt
if __name__ == "__main__":
    # Example: Test a single model on all conversation threads
    # test_model_on_database("claude-3.5-haiku")

    # Example: Test all models on a single thread
    compare_models("Tricky GPU error driver update problem")

    # Example: Test a specific model with and without system prompt on a chosen thread
    # test_model_with_without_system_prompt("claude-4-sonnet", "Unity basics")
