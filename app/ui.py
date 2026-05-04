import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Resume Job Matcher", page_icon="💼")

st.title("💼 Resume Job Matcher")

# Inputs
resume = st.text_area("Paste your resume")
desc = st.text_area("Optional description")

# Button
if st.button("Match Jobs"):

    if not resume.strip():
        st.warning("Please enter resume text")
    else:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/match",
                json={
                    "resume_text": resume,
                    "description": desc
                },
                timeout=10
            )

            # Check API response status
            if response.status_code != 200:
                st.error(f"❌ API Error: {response.status_code}")
                st.text(response.text)

            else:
                try:
                    data = response.json()

                    if "matches" not in data:
                        st.error("Invalid response from API")
                        st.text(data)

                    else:
                        st.success("✅ Matches found")

                        for job in data["matches"]:
                            st.markdown(f"### {job['Job Title']}")
                            st.write(f"📊 Score: {job['score']:.3f}")
                            st.write(f"🛠 Skills: {job['Required Skills']}")
                            st.write(f"🎓 Education: {job['Education Requirement']}")
                            st.write(f"💼 Experience: {job['Experience Years']} years")
                            st.write("---")

                except Exception as e:
                    st.error("❌ Failed to parse API response")
                    st.text(str(e))
                    st.text(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend API. Make sure FastAPI is running on port 8000.")

        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Backend might be slow.")

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")