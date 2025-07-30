import streamlit as st
import datetime
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import json
import sys
import traceback
from qa_pairs.slack_qa_generator import main as slack_qa_main

load_dotenv()

# Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def check_slack_conversations_exists():
    """Check if slack_conversations.md exists in S3"""
    try:
        s3 = boto3.client("s3")
        s3.head_object(
            Bucket=S3_BUCKET_NAME, Key="slack_conversations/slack_conversations.md"
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            st.error(f"Error checking for slack_conversations.md: {e}")
            return False
    except Exception as e:
        st.error(f"Error checking for slack_conversations.md: {e}")
        return False


def get_qa_files():
    """Get all Q&A JSON files from S3 slack_conversations folder"""
    try:
        s3 = boto3.client("s3")
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET_NAME, Prefix="slack_conversations/slack_qa_pairs_"
        )

        qa_files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                if obj["Key"].endswith(".json") and "slack_qa_pairs_" in obj["Key"]:
                    qa_files.append(obj["Key"])

        return sorted(qa_files, reverse=True)  # Most recent first
    except Exception as e:
        st.error(f"Error accessing S3 Q&A files: {e}")
        return []


def load_qa_file(file_path):
    """Load Q&A pairs from S3 JSON file"""
    try:
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=file_path)
        content = response["Body"].read().decode("utf-8")
        data = json.loads(content)
        return data if isinstance(data, list) else data.get("qa_pairs", [])
    except Exception as e:
        st.error(f"Error loading Q&A file from S3: {e}")
        return []


def save_qa_file(file_path, qa_pairs):
    """Save Q&A pairs to S3 JSON file"""
    try:
        s3 = boto3.client("s3")
        content = json.dumps(qa_pairs, indent=2, ensure_ascii=False)

        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_path,
            Body=content,
            ContentType="application/json",
        )
        return True
    except Exception as e:
        st.error(f"Error saving Q&A file to S3: {e}")
        return False


def load_approved_qa_pairs():
    """Load approved Q&A pairs from S3"""
    approved_key = "slack_conversations/approved_qa_pairs.json"
    try:
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=approved_key)
        content = response["Body"].read().decode("utf-8")
        data = json.loads(content)
        return data.get("qa_pairs", []) if isinstance(data, dict) else data
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []  # File doesn't exist yet
        else:
            st.error(f"Error loading approved Q&A pairs from S3: {e}")
            return []
    except Exception as e:
        st.error(f"Error loading approved Q&A pairs: {e}")
        return []


def save_approved_qa_pairs(approved_pairs):
    """Save approved Q&A pairs to S3"""
    approved_key = "slack_conversations/approved_qa_pairs.json"
    try:
        s3 = boto3.client("s3")

        # Create metadata structure
        data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_pairs": len(approved_pairs),
            "qa_pairs": approved_pairs,
        }

        content = json.dumps(data, indent=2, ensure_ascii=False)

        # Add metadata to S3 object
        metadata = {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_pairs": str(len(approved_pairs)),
            "content_type": "approved_qa_pairs",
        }

        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=approved_key,
            Body=content,
            ContentType="application/json",
            Metadata=metadata,
        )
        return True
    except Exception as e:
        st.error(f"Error saving approved Q&A pairs to S3: {e}")
        return False


def remove_current_qa_pair():
    """Remove current Q&A pair from the source file"""
    if (
        st.session_state.current_qa_file
        and 0 <= st.session_state.current_qa_index < len(st.session_state.qa_pairs)
    ):
        # Remove the current pair
        st.session_state.qa_pairs.pop(st.session_state.current_qa_index)

        # Save updated file
        if save_qa_file(st.session_state.current_qa_file, st.session_state.qa_pairs):
            # Adjust index if necessary
            if st.session_state.current_qa_index >= len(st.session_state.qa_pairs):
                st.session_state.current_qa_index = max(
                    0, len(st.session_state.qa_pairs) - 1
                )
            return True
    return False


def approve_qa_pair(qa_pair):
    """Add Q&A pair to approved list"""
    # Load current approved pairs
    approved_pairs = load_approved_qa_pairs()

    # Create clean Q&A pair without original conversation and metadata
    qa_pair_with_metadata = {
        "question": qa_pair.get("question", ""),
        "answers": qa_pair.get("answers", []),
    }

    # Add approval metadata
    qa_pair_with_metadata["approved_at"] = datetime.datetime.now().isoformat()
    qa_pair_with_metadata["source_file"] = st.session_state.current_qa_file
    qa_pair_with_metadata["original_index"] = st.session_state.current_qa_index

    # Add to approved list
    approved_pairs.append(qa_pair_with_metadata)

    # Save approved pairs
    if save_approved_qa_pairs(approved_pairs):
        # Remove from source file
        return remove_current_qa_pair()
    return False


def run_qa_generator_and_upload():
    """Run the Q&A generator using Slack conversations from S3"""
    # First check if slack_conversations.md exists in S3
    if not check_slack_conversations_exists():
        st.error(
            "❌ Could not find `slack_conversations/slack_conversations.md` in S3. Please upload the Slack conversations file first."
        )
        return

    st.info("Generating Q&A pairs from Slack conversations in S3...")
    with st.spinner("Processing conversations and uploading to S3..."):
        try:
            # Import and run the Q&A generator with S3 input
            sys.path.append(os.path.join(os.getcwd(), "qa_pairs"))

            # Run Q&A generator with S3 input (this will save directly to S3)
            success = slack_qa_main()

            if success:
                st.success("✅ Q&A pairs generated and uploaded to S3!")
            else:
                st.warning(
                    "⚠️ Q&A generation completed but no pairs were generated or saved."
                )

        except Exception as e:
            st.error(f"❌ Error running Q&A generator: {e}")
            st.error(f"Details: {traceback.format_exc()}")

    # Refresh the dashboard
    st.cache_data.clear()
    st.rerun()


def display_qa_pair_review_tab():
    """Display the Q&A Pair Review tab content"""
    st.header("📋 Q&A Pair Review")

    # Initialize session state for Q&A review
    if "current_qa_file" not in st.session_state:
        st.session_state.current_qa_file = None
    if "current_qa_index" not in st.session_state:
        st.session_state.current_qa_index = 0
    if "qa_pairs" not in st.session_state:
        st.session_state.qa_pairs = []
    if "approved_qa_pairs" not in st.session_state:
        st.session_state.approved_qa_pairs = []

    # File selection
    qa_files = get_qa_files()

    # Check if source file exists
    slack_file_exists = check_slack_conversations_exists()

    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Q&A Files", key="refresh_qa"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        button_disabled = not slack_file_exists
        button_text = (
            "🤖 Generate Q&A Pairs from S3"
            if slack_file_exists
            else "🚫 No Slack File in S3"
        )
        if st.button(button_text, key="generate_qa", disabled=button_disabled):
            run_qa_generator_and_upload()

    # Status indicator
    if slack_file_exists:
        st.success("✅ `slack_conversations/slack_conversations.md` found in S3")
    else:
        st.warning("⚠️ `slack_conversations/slack_conversations.md` not found in S3")

    if not qa_files:
        st.info(
            "No Q&A Pairs files found in S3 slack_conversations folder. Click 'Generate Q&A Pairs from S3' to create them."
        )
    else:
        # File selector
        selected_file = st.selectbox(
            "Select Q&A file to review:", qa_files, key="qa_file_selector"
        )

        # Load file if changed or first time
        if selected_file != st.session_state.current_qa_file:
            st.session_state.current_qa_file = selected_file
            st.session_state.qa_pairs = load_qa_file(selected_file)
            st.session_state.current_qa_index = 0

        if st.session_state.qa_pairs:
            # Check if this file has original conversations
            has_original_conversations = False
            if st.session_state.qa_pairs:
                has_original_conversations = any(
                    "original_conversation" in pair
                    for pair in st.session_state.qa_pairs
                )

            # Display file info
            if has_original_conversations:
                st.success(
                    "✅ This file includes original Slack conversations for review"
                )
            else:
                st.info(
                    "ℹ️ This file was generated before conversation tracking was implemented"
                )

            # Display progress
            total_pairs = len(st.session_state.qa_pairs)
            current_index = st.session_state.current_qa_index

            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.progress((current_index + 1) / total_pairs)
                st.caption(f"Reviewing pair {current_index + 1} of {total_pairs}")
            with col2:
                # Navigation buttons
                if st.button("⬅️ Previous", disabled=(current_index == 0)):
                    st.session_state.current_qa_index = max(0, current_index - 1)
                    st.rerun()
            with col3:
                if st.button("➡️ Next", disabled=(current_index >= total_pairs - 1)):
                    st.session_state.current_qa_index = min(
                        total_pairs - 1, current_index + 1
                    )
                    st.rerun()
            with col4:
                # Jump to specific index
                jump_to_index = st.number_input(
                    "Jump to:",
                    min_value=1,
                    max_value=total_pairs,
                    value=current_index + 1,
                    step=1,
                    key=f"jump_to_{current_index}",
                    help="Enter a pair number to jump directly to it",
                )
                if st.button("🎯 Go", key=f"jump_button_{current_index}"):
                    st.session_state.current_qa_index = jump_to_index - 1
                    st.rerun()

            st.markdown("---")

            # Display current Q&A pair
            if current_index < len(st.session_state.qa_pairs):
                current_pair = st.session_state.qa_pairs[current_index]

                st.subheader("📝 Current Q&A Pair")

                # Editable question
                edited_question = st.text_area(
                    "Question:",
                    value=current_pair.get("question", ""),
                    height=100,
                    key=f"question_edit_{current_index}",
                )

                # Editable answers
                st.write("**Answers:**")
                answers = current_pair.get("answers", [])
                edited_answers = []

                for i, answer in enumerate(answers):
                    edited_answer = st.text_area(
                        f"Answer {i + 1}:",
                        value=answer,
                        height=80,
                        key=f"answer_edit_{current_index}_{i}",
                    )
                    edited_answers.append(edited_answer)

                # Button to add new answer
                if st.button("➕ Add Answer", key=f"add_answer_{current_index}"):
                    edited_answers.append("")
                    # Update the Q&A pair with new empty answer
                    updated_pair = {
                        "question": edited_question,
                        "answers": edited_answers,
                    }
                    # Preserve original conversation if it exists
                    if "original_conversation" in current_pair:
                        updated_pair["original_conversation"] = current_pair[
                            "original_conversation"
                        ]
                    if "conversation_index" in current_pair:
                        updated_pair["conversation_index"] = current_pair[
                            "conversation_index"
                        ]
                    if "total_conversations" in current_pair:
                        updated_pair["total_conversations"] = current_pair[
                            "total_conversations"
                        ]
                    if "generated_at" in current_pair:
                        updated_pair["generated_at"] = current_pair["generated_at"]

                    st.session_state.qa_pairs[current_index] = updated_pair
                    save_qa_file(
                        st.session_state.current_qa_file, st.session_state.qa_pairs
                    )
                    st.rerun()

                # Original Conversation Expandable Section
                original_conversation = current_pair.get("original_conversation")
                if original_conversation:
                    with st.expander(
                        "📜 View Original Slack Conversation", expanded=False
                    ):
                        st.markdown("**Original Conversation Thread:**")

                        # Add metadata if available
                        conversation_metadata = []
                        if "conversation_index" in current_pair:
                            conversation_metadata.append(
                                f"Conversation #{current_pair['conversation_index']}"
                            )
                        if "total_conversations" in current_pair:
                            conversation_metadata.append(
                                f"of {current_pair['total_conversations']} total"
                            )
                        if "generated_at" in current_pair:
                            conversation_metadata.append(
                                f"Generated: {current_pair['generated_at'][:19].replace('T', ' ')}"
                            )

                        if conversation_metadata:
                            st.caption(" • ".join(conversation_metadata))

                        # Display the conversation in a code block for better formatting
                        st.text_area(
                            "Conversation Content:",
                            value=original_conversation,
                            height=300,
                            key=f"original_conversation_{current_index}",
                            disabled=True,
                            help="This is the original Slack conversation thread that was used to generate this Q&A pair",
                        )
                else:
                    st.info(
                        "ℹ️ Original conversation not available for this Q&A pair (generated before conversation tracking was implemented)"
                    )

                st.markdown("---")

                # Action buttons
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button(
                        "✅ Approve", key=f"approve_{current_index}", type="primary"
                    ):
                        # Update the current pair with edits
                        updated_pair = {
                            "question": edited_question,
                            "answers": [
                                ans for ans in edited_answers if ans.strip()
                            ],  # Remove empty answers
                        }

                        # Preserve original conversation and metadata
                        for key in [
                            "original_conversation",
                            "conversation_index",
                            "total_conversations",
                            "generated_at",
                        ]:
                            if key in current_pair:
                                updated_pair[key] = current_pair[key]

                        if updated_pair["question"].strip() and updated_pair["answers"]:
                            if approve_qa_pair(updated_pair):
                                st.success("Q&A pair approved and added to database!")
                                st.rerun()
                            else:
                                st.error("Failed to approve Q&A pair")
                        else:
                            st.warning("Question and at least one answer are required")

                with col2:
                    if st.button("❌ Reject", key=f"reject_{current_index}"):
                        if remove_current_qa_pair():
                            st.success("Q&A pair rejected and removed!")
                            st.rerun()
                        else:
                            st.error("Failed to reject Q&A pair")

                with col3:
                    if st.button("💾 Save Edits", key=f"save_{current_index}"):
                        # Update the current pair with edits
                        updated_pair = {
                            "question": edited_question,
                            "answers": [
                                ans for ans in edited_answers if ans.strip()
                            ],  # Remove empty answers
                        }

                        # Preserve original conversation and metadata
                        for key in [
                            "original_conversation",
                            "conversation_index",
                            "total_conversations",
                            "generated_at",
                        ]:
                            if key in current_pair:
                                updated_pair[key] = current_pair[key]

                        if updated_pair["question"].strip() and updated_pair["answers"]:
                            st.session_state.qa_pairs[current_index] = updated_pair
                            if save_qa_file(
                                st.session_state.current_qa_file,
                                st.session_state.qa_pairs,
                            ):
                                st.success("Changes saved!")
                            else:
                                st.error("Failed to save changes")
                        else:
                            st.warning("Question and at least one answer are required")

                with col4:
                    if st.button("⏭️ Skip", key=f"skip_{current_index}"):
                        if current_index < total_pairs - 1:
                            st.session_state.current_qa_index += 1
                            st.rerun()
                        else:
                            st.info("No more pairs to review")

                st.markdown("---")

                # Statistics
                approved_pairs = load_approved_qa_pairs()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Remaining to Review", total_pairs)
                with col2:
                    st.metric("Approved Pairs", len(approved_pairs))
                with col3:
                    if total_pairs > 0:
                        completion_rate = (
                            (len(approved_pairs)) / (len(approved_pairs) + total_pairs)
                        ) * 100
                        st.metric("Completion Rate", f"{completion_rate:.1f}%")

            else:
                st.success("🎉 All Q&A pairs in this file have been reviewed!")

                # Show option to load another file
                remaining_files = [
                    f for f in qa_files if f != st.session_state.current_qa_file
                ]
                if remaining_files:
                    st.info("Select another file to continue reviewing.")
                else:
                    st.info("All Q&A files have been processed!")

        else:
            st.warning("No Q&A pairs found in the selected file.")

    st.markdown("---")

    # Display approved pairs management
    st.subheader("📊 Approved Q&A Pairs Management")
    approved_pairs = load_approved_qa_pairs()
    if approved_pairs:
        st.write(f"**Total Approved Pairs:** {len(approved_pairs)}")

        # Initialize session state for approved pairs navigation
        if "current_approved_index" not in st.session_state:
            st.session_state.current_approved_index = 0

        # Ensure index is within bounds
        if st.session_state.current_approved_index >= len(approved_pairs):
            st.session_state.current_approved_index = max(0, len(approved_pairs) - 1)

        # Control buttons and navigation
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

        with col1:
            if st.button("🔄 Refresh", key="refresh_approved"):
                st.cache_data.clear()
                st.rerun()

        with col2:
            # Previous button
            if st.button(
                "⬅️ Previous",
                disabled=(st.session_state.current_approved_index == 0),
                key="prev_approved",
            ):
                st.session_state.current_approved_index = max(
                    0, st.session_state.current_approved_index - 1
                )
                st.rerun()

        with col3:
            # Next button
            if st.button(
                "➡️ Next",
                disabled=(
                    st.session_state.current_approved_index >= len(approved_pairs) - 1
                ),
                key="next_approved",
            ):
                st.session_state.current_approved_index = min(
                    len(approved_pairs) - 1, st.session_state.current_approved_index + 1
                )
                st.rerun()

        with col4:
            # Jump to specific index
            jump_to_index = st.number_input(
                "Jump to:",
                min_value=1,
                max_value=len(approved_pairs),
                value=st.session_state.current_approved_index + 1,
                step=1,
                key="jump_to_approved",
                help="Enter a pair number to jump directly to it",
            )

        with col5:
            if st.button("🎯 Go", key="jump_button_approved"):
                st.session_state.current_approved_index = jump_to_index - 1
                st.rerun()

        # Search functionality
        search_approved = st.text_input(
            "🔍 Search approved pairs:",
            placeholder="Search by question or answer...",
            key="search_approved_pairs",
        )

        # Filter approved pairs based on search
        filtered_pairs = approved_pairs
        if search_approved:
            search_lower = search_approved.lower()
            filtered_pairs = [
                pair
                for pair in approved_pairs
                if (
                    search_lower in pair.get("question", "").lower()
                    or search_lower in str(pair.get("answers", [])).lower()
                    or search_lower in pair.get("answer", "").lower()
                )
            ]

        st.markdown("---")

        # Display current pair or search results
        if search_approved:
            # Show search results
            if filtered_pairs:
                st.write(f"**Search Results: {len(filtered_pairs)} pairs found**")

                for i, pair in enumerate(filtered_pairs):
                    # Find original index in the full list
                    original_index = approved_pairs.index(pair)
                    approved_at = pair.get("approved_at", "Unknown")
                    source_file = pair.get("source_file", "Unknown")

                    # Format approval date
                    try:
                        dt = datetime.datetime.fromisoformat(approved_at)
                        approved_at_formatted = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception as e:
                        approved_at_formatted = approved_at
                        st.error(f"Error in formatting approval date: {e}")

                    # Create container for each search result
                    with st.container():
                        st.markdown(
                            f"**#{original_index + 1} - {pair.get('question', 'No question')[:80]}...** *(Approved: {approved_at_formatted})*"
                        )

                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.write("**Question:**")
                            st.write(pair.get("question", "No question available"))

                            # Handle both single answer and multiple answers format
                            if "answers" in pair and isinstance(pair["answers"], list):
                                st.write("**Answers:**")
                                for j, answer in enumerate(pair["answers"]):
                                    st.write(f"{j + 1}. {answer}")
                            elif "answer" in pair:
                                st.write("**Answer:**")
                                st.write(pair.get("answer", "No answer available"))
                            else:
                                st.write("**Answer:** No answer available")

                        with col2:
                            st.write("**Metadata:**")
                            st.write(f"Index: #{original_index + 1}")
                            st.write(f"Approved: {approved_at_formatted}")
                            if source_file != "Unknown":
                                st.write(f"Source: {source_file.split('/')[-1]}")

                            # Delete button for approved pairs (single click)
                            if st.button(
                                "🗑️ Delete",
                                key=f"delete_approved_search_{original_index}",
                                help="Delete this approved Q&A pair",
                            ):
                                # Remove the pair from approved list
                                updated_approved = [
                                    p
                                    for j, p in enumerate(approved_pairs)
                                    if j != original_index
                                ]

                                # Save updated approved pairs
                                if save_approved_qa_pairs(updated_approved):
                                    st.success(
                                        "✅ Approved Q&A pair deleted successfully!"
                                    )
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete approved Q&A pair.")

                        # Add separator between pairs (except for the last one)
                        if i < len(filtered_pairs) - 1:
                            st.markdown("---")
            else:
                st.info("No approved pairs match your search criteria.")
        else:
            # Show single pair navigation
            if approved_pairs:
                current_index = st.session_state.current_approved_index
                pair = approved_pairs[current_index]
                approved_at = pair.get("approved_at", "Unknown")
                source_file = pair.get("source_file", "Unknown")

                # Progress indicator
                st.progress((current_index + 1) / len(approved_pairs))
                st.caption(f"Viewing pair {current_index + 1} of {len(approved_pairs)}")

                # Format approval date
                try:
                    dt = datetime.datetime.fromisoformat(approved_at)
                    approved_at_formatted = dt.strftime("%Y-%m-%d %H:%M")
                except Exception as e:
                    approved_at_formatted = approved_at
                    st.error(f"Error in formatting approval date: {e}")

                # Create container for current pair
                with st.container():
                    st.markdown(
                        f"**#{current_index + 1} - {pair.get('question', 'No question')[:80]}...** *(Approved: {approved_at_formatted})*"
                    )

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.write("**Question:**")
                        st.write(pair.get("question", "No question available"))

                        # Handle both single answer and multiple answers format
                        if "answers" in pair and isinstance(pair["answers"], list):
                            st.write("**Answers:**")
                            for j, answer in enumerate(pair["answers"]):
                                st.write(f"{j + 1}. {answer}")
                        elif "answer" in pair:
                            st.write("**Answer:**")
                            st.write(pair.get("answer", "No answer available"))
                        else:
                            st.write("**Answer:** No answer available")

                    with col2:
                        st.write("**Metadata:**")
                        st.write(f"Index: #{current_index + 1}")
                        st.write(f"Approved: {approved_at_formatted}")
                        if source_file != "Unknown":
                            st.write(f"Source: {source_file.split('/')[-1]}")

                        # Delete button for approved pairs (single click)
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_approved_{current_index}",
                            help="Delete this approved Q&A pair",
                        ):
                            # Remove the pair from approved list
                            updated_approved = [
                                p
                                for j, p in enumerate(approved_pairs)
                                if j != current_index
                            ]

                            # Save updated approved pairs
                            if save_approved_qa_pairs(updated_approved):
                                st.success("✅ Approved Q&A pair deleted successfully!")
                                # Adjust index if necessary
                                if st.session_state.current_approved_index >= len(
                                    updated_approved
                                ):
                                    st.session_state.current_approved_index = max(
                                        0, len(updated_approved) - 1
                                    )
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete approved Q&A pair.")
            else:
                st.info("No approved pairs to display.")
    else:
        st.info(
            "No approved Q&A pairs yet. Approve some pairs from the review section above to see them here."
        )
