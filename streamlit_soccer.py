import streamlit as st
import pandas as pd
import os

# Setup
UPLOAD_FOLDER = "uploaded_videos"
CSV_FILE = "ratings.csv"
METADATA_FILE = "video_metadata.csv"

# Define metric descriptions
metrics = {
    "Action Accuracy": "How well the commentary captures the action in the video.",
    "Player Identification": "How accurately the commentary identifies the players involved.",
    "Scorecard Relevance": "How well the commentary reflects the score or state of the game.",
    "Event Chronology": "How well the sequence of events in the commentary matches the video.",
    "Commentary Quality": "The overall relevance, fluency, and engagement level of the commentary."
}

# Create directories and files if not present
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Video Name", "Action Accuracy", "Player Identification", "Scorecard Relevance",
                          "Event Chronology", "Commentary Quality", "Preferred Model"]).to_csv(CSV_FILE, index=False)

if not os.path.exists(METADATA_FILE):
    pd.DataFrame(columns=["Video Name", "MatchTime Commentary", "Llava-Qwen Commentary"]).to_csv(METADATA_FILE, index=False)

# Load existing data
ratings_df = pd.read_csv(CSV_FILE)
metadata_df = pd.read_csv(METADATA_FILE)

# User Mode Selection
st.sidebar.title("Mode Selection")
mode = st.sidebar.radio("Select Mode", ["User Mode", "Admin Mode"])

# User Mode: Evaluate Videos
if mode == "User Mode":
    st.title("Evaluate Videos")
    if len(metadata_df) > 0:
        video_files = metadata_df["Video Name"].unique()

        if video_files.any():
            selected_video = st.selectbox("Select a video to evaluate", video_files)

            if selected_video:
                # Load commentary data for the selected video
                selected_metadata = metadata_df[metadata_df["Video Name"] == selected_video].iloc[0]
                
                # Display selected video
                st.video(os.path.join(UPLOAD_FOLDER, selected_video))
                
                # Display commentaries
                st.subheader("Generated Commentary for MatchTime")
                st.text_area("MatchTime Commentary Output", value=selected_metadata["MatchTime Commentary"], height=100, disabled=True)

                st.subheader("Generated Commentary for Llava-Qwen-Interleave")
                st.text_area("Llava-Qwen Commentary Output", value=selected_metadata["Llava-Qwen Commentary"], height=100, disabled=True)

                # Rating Section with Descriptions
                st.subheader("Evaluate Commentary Metrics (for Llava-Qwen-Interleave)")
                scores = {}
                for metric, description in metrics.items():
                    st.markdown(f"**{metric}**")
                    st.write(description)
                    scores[metric] = st.slider(f"Rate {metric}", 1, 10, 1)

                # Preference Selection
                st.subheader("Which Model Generation Do You Prefer?")
                preferred_model = st.radio("Preferred Model", ["MatchTime", "Llava-Qwen-Interleave"])

                # Submit Ratings
                if st.button("Submit Ratings"):
                    # Save to CSV
                    new_rating = {
                        "Video Name": selected_video,
                        **scores,
                        "Preferred Model": preferred_model,
                    }
                    ratings_df = ratings_df.append(new_rating, ignore_index=True)
                    ratings_df.to_csv(CSV_FILE, index=False)
                    st.success("Your ratings have been submitted and saved!")

# Admin Mode: Upload and Manage Videos
elif mode == "Admin Mode":
    st.title("Admin Mode")

    # Upload Section
    st.header("Upload Video and Generated Commentaries")
    uploaded_video = st.file_uploader("Upload Soccer Video", type=["mp4", "avi", "mov"], accept_multiple_files=False)
    matchtime_commentary = st.text_area("Paste MatchTime Generated Commentary")
    llava_qwen_commentary = st.text_area("Paste Llava-Qwen-Interleave Generated Commentary")

    if uploaded_video and matchtime_commentary and llava_qwen_commentary:
        # Save the uploaded video
        video_path = os.path.join(UPLOAD_FOLDER, uploaded_video.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_video.read())
        
        # Save the commentary information in the metadata CSV
        new_metadata = pd.DataFrame({
            "Video Name": [uploaded_video.name],
            "MatchTime Commentary": [matchtime_commentary],
            "Llava-Qwen Commentary": [llava_qwen_commentary]
        })
        new_metadata.to_csv(METADATA_FILE, mode="a", header=False, index=False)
        
        st.success("Video and commentaries uploaded successfully!")

    # Manage Uploaded Videos
    st.header("Manage Uploaded Videos")
    video_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith((".mp4", ".avi", ".mov"))]

    if video_files:
        st.subheader("Existing Videos")
        selected_video_to_delete = st.selectbox("Select a video to delete", video_files)

        if st.button("Delete Selected Video"):
            # Delete video file
            video_path = os.path.join(UPLOAD_FOLDER, selected_video_to_delete)
            if os.path.exists(video_path):
                os.remove(video_path)
                st.success(f"Deleted video file: {selected_video_to_delete}")

            # Remove from metadata
            metadata_df = metadata_df[metadata_df["Video Name"] != selected_video_to_delete]
            metadata_df.to_csv(METADATA_FILE, index=False)

            # Remove from ratings
            ratings_df = ratings_df[ratings_df["Video Name"] != selected_video_to_delete]
            ratings_df.to_csv(CSV_FILE, index=False)

            st.success(f"Removed metadata and ratings for: {selected_video_to_delete}")



