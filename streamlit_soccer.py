import streamlit as st
import pandas as pd
import os

# Setup
CSV_FILE = "ratings.csv"

# Initialize CSV file if not present
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Video Name", "Action Accuracy", "Player Identification",
                          "Scorecard Relevance", "Event Chronology", 
                          "Commentary Quality", "Preferred Model"]).to_csv(CSV_FILE, index=False)

# Define metric descriptions
metrics = {
    "Action Accuracy": "How well the commentary captures the action in the video.",
    "Player Identification": "How accurately the commentary identifies the players involved.",
    "Scorecard Relevance": "How well the commentary reflects the score or state of the game.",
    "Event Chronology": "How well the sequence of events in the commentary matches the video.",
    "Commentary Quality": "The overall relevance, fluency, and engagement level of the commentary."
}

# User Mode Selection with Passcode for Admin Mode
st.sidebar.title("Mode Selection")
mode = st.sidebar.radio("Select Mode", ["User Mode", "Admin Mode"])

# User Mode: Evaluate Videos
if mode == "User Mode":
    st.title("Evaluate Videos")
    st.header("Submit Your Ratings")

    # Video selection
    video_name = st.text_input("Enter the name of the video being evaluated")

    # Rating section
    if video_name:
        scores = {}
        for metric, description in metrics.items():
            st.markdown(f"**{metric}**")
            st.write(description)
            scores[metric] = st.slider(f"Rate {metric}", 1, 10, 5)

        # Preference Selection
        st.subheader("Which Model Generation Do You Prefer?")
        preferred_model = st.radio("Preferred Model", ["MatchTime", "Llava-Qwen-Interleave"])

        # Submit Ratings
        if st.button("Submit Ratings"):
            # Save to CSV
            new_rating = {
                "Video Name": video_name,
                **scores,
                "Preferred Model": preferred_model,
            }
            ratings_df = pd.read_csv(CSV_FILE)
            ratings_df = pd.concat([ratings_df, pd.DataFrame([new_rating])], ignore_index=True)
            ratings_df.to_csv(CSV_FILE, index=False)
            st.success("Your ratings have been submitted and saved!")

# Admin Mode: Upload and Manage CSV
elif mode == "Admin Mode":
    st.title("Admin Mode")

    # Admin Passcode Input
    admin_passcode = st.sidebar.text_input("Enter Admin Passcode", type="password")
    if admin_passcode == "travis_gogh":
        st.success("Access granted to Admin Mode")

        # Display CSV Download Option
        st.header("Download Ratings CSV")
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as file:
                st.download_button(
                    label="Download Ratings CSV",
                    data=file,
                    file_name="ratings.csv",
                    mime="text/csv",
                )

        # Delete CSV File Option
        st.header("Delete Ratings CSV")
        if st.button("Delete Ratings CSV"):
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
                # Reinitialize empty CSV
                pd.DataFrame(columns=["Video Name", "Action Accuracy", "Player Identification",
                                      "Scorecard Relevance", "Event Chronology", 
                                      "Commentary Quality", "Preferred Model"]).to_csv(CSV_FILE, index=False)
                st.success("Ratings CSV deleted and reinitialized.")
            else:
                st.warning("No CSV file found to delete.")
    else:
        st.error("Invalid passcode. Please try again.")



