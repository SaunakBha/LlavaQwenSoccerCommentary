import streamlit as st
import pandas as pd
import os

UPLOAD_FOLDER = "uploaded_videos"
CSV_FILE = "ratings.csv"
METADATA_FILE = "video_metadata.csv"

metrics = {
    "Action Accuracy": "How well the commentary captures the action in the video.",
    "Player Identification": "How accurately the commentary identifies the players involved.",
    "Scorecard Relevance": "How well the commentary reflects the score or state of the game.",
    "Event Chronology": "How well the sequence of events in the commentary matches the video.",
    "Commentary Quality": "The overall relevance, fluency, and engagement level of the commentary."
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Video Name", "Action Accuracy", "Player Identification", "Scorecard Relevance",
                          "Event Chronology", "Commentary Quality", "Preferred Model"]).to_csv(CSV_FILE, index=False)

if not os.path.exists(METADATA_FILE):
    pd.DataFrame(columns=["Video Name", "MatchTime Commentary", "Llava-Qwen Commentary"]).to_csv(METADATA_FILE, index=False)

ratings_df = pd.read_csv(CSV_FILE)
metadata_df = pd.read_csv(METADATA_FILE)

st.sidebar.title("Mode Selection")
mode = st.sidebar.radio("Select Mode", ["User Mode", "Admin Mode"])

if mode == "Admin Mode":

    admin_passcode = st.sidebar.text_input("Enter Admin Passcode", type="password")
    if admin_passcode == "travis_gogh":
        st.success("Access granted to Admin Mode")


        st.title("Admin Mode")


        st.header("Upload Video and Generated Commentaries")
        uploaded_video = st.file_uploader("Upload Soccer Video", type=["mp4", "avi", "mov"], accept_multiple_files=False)
        matchtime_commentary = st.text_area("Paste MatchTime Generated Commentary")
        llava_qwen_commentary = st.text_area("Paste Llava-Qwen-Interleave Generated Commentary")

        if uploaded_video and matchtime_commentary and llava_qwen_commentary:
  
            video_path = os.path.join(UPLOAD_FOLDER, uploaded_video.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_video.read())
            
            new_metadata = pd.DataFrame({
                "Video Name": [uploaded_video.name],
                "MatchTime Commentary": [matchtime_commentary],
                "Llava-Qwen Commentary": [llava_qwen_commentary]
            })
            new_metadata.to_csv(METADATA_FILE, mode="a", header=False, index=False)
            
            st.success("Video and commentaries uploaded successfully!")

        st.header("Manage Uploaded Videos")
        video_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith((".mp4", ".avi", ".mov"))]

        if video_files:
            st.subheader("Existing Videos")
            selected_video_to_delete = st.selectbox("Select a video to delete", video_files)

            if st.button("Delete Selected Video"):

                video_path = os.path.join(UPLOAD_FOLDER, selected_video_to_delete)
                if os.path.exists(video_path):
                    os.remove(video_path)
                    st.success(f"Deleted video file: {selected_video_to_delete}")

                metadata_df = metadata_df[metadata_df["Video Name"] != selected_video_to_delete]
                metadata_df.to_csv(METADATA_FILE, index=False)

                ratings_df = ratings_df[ratings_df["Video Name"] != selected_video_to_delete]
                ratings_df.to_csv(CSV_FILE, index=False)

                st.success(f"Removed metadata and ratings for: {selected_video_to_delete}")

        st.header("Access and Manage CSV Files")
        
        st.subheader("Download CSV Files")
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as file:
                st.download_button(
                    label="Download Ratings CSV",
                    data=file,
                    file_name="ratings.csv",
                    mime="text/csv",
                )
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "rb") as file:
                st.download_button(
                    label="Download Metadata CSV",
                    data=file,
                    file_name="video_metadata.csv",
                    mime="text/csv",
                )
        
        st.subheader("Delete CSV Files")
        if st.button("Delete All CSV Files"):
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
                pd.DataFrame(columns=["Video Name", "Action Accuracy", "Player Identification", "Scorecard Relevance",
                                      "Event Chronology", "Commentary Quality", "Preferred Model"]).to_csv(CSV_FILE, index=False)
                st.success("Ratings CSV deleted and reinitialized.")

            if os.path.exists(METADATA_FILE):
                os.remove(METADATA_FILE)
                pd.DataFrame(columns=["Video Name", "MatchTime Commentary", "Llava-Qwen Commentary"]).to_csv(METADATA_FILE, index=False)
                st.success("Metadata CSV deleted and reinitialized.")
    else:
        st.error("Invalid passcode. Please try again.")

if mode == "User Mode":
    st.title("Evaluate Videos")
    if len(metadata_df) > 0:
        video_files = metadata_df["Video Name"].unique()

        if video_files.any():
            selected_video = st.selectbox("Select a video to evaluate", video_files)

            if selected_video:

                selected_metadata = metadata_df[metadata_df["Video Name"] == selected_video].iloc[0]
                
                st.video(os.path.join(UPLOAD_FOLDER, selected_video))
                
                st.subheader("Generated Commentary for MatchTime")
                st.text_area("MatchTime Commentary Output", value=selected_metadata["MatchTime Commentary"], height=100, disabled=True)

                st.subheader("Generated Commentary for Llava-Qwen-Interleave")
                st.text_area("Llava-Qwen Commentary Output", value=selected_metadata["Llava-Qwen Commentary"], height=100, disabled=True)

                st.subheader("Evaluate Commentary Metrics (for Llava-Qwen-Interleave)")
                scores = {}
                for metric, description in metrics.items():
                    st.markdown(f"**{metric}**")
                    st.write(description)
                    scores[metric] = st.slider(f"Rate {metric}", 1, 10, 1)

                st.subheader("Which Model Generation Do You Prefer?")
                preferred_model = st.radio("Preferred Model", ["MatchTime", "Llava-Qwen-Interleave"])

                if st.button("Submit Ratings"):

                    new_rating = {
                        "Video Name": selected_video,
                        **scores,
                        "Preferred Model": preferred_model,
                    }
                    ratings_df = pd.concat([ratings_df, pd.DataFrame([new_rating])], ignore_index=True)
                    ratings_df.to_csv(CSV_FILE, index=False)
                    st.success("Your ratings have been submitted and saved!")



