BA261 Optional Streamlit Experiment — Student Starter
This packet accompanies an entirely optional, ungraded end-of-semester activity for BA261: Introduction to Data Analytics for Accounting.
What to use
`streamlit_app.py`: a starter interactive Uber pickup visualization including a 24-hour animated heat map
`requirements.txt`: the Python dependencies for Streamlit Community Cloud
Follow the detailed instructions in the optional Canvas lesson page to create your own GitHub repository, upload these two files, and publish the app.
You do not need to install Python locally. You can also just watch the instructor's demonstration and skip setup entirely. If you want to build a different idea using AI, the optional Canvas lesson includes sample prompts for that too.
Data
The script loads the first 100,000 records from a historical September 2014 NYC Uber pickup dataset used in Streamlit's public tutorial. The data is downloaded at app runtime from the public Streamlit demo S3 bucket; no private credentials or data upload required. The final date of the 100,000-record sample may be incomplete.
https://docs.streamlit.io/get-started/tutorials/create-an-app
https://github.com/streamlit/demo-uber-nyc-pickups
Safety and interpretation
Only use public or fictional data in publicly deployed applications. Do not upload real student, customer, employer, or personal financial information, or secret passwords and API keys. AI-generated code needs testing; an attractive visualization does not prove a causal explanation.
Credits
Streamlit provided the original Uber dataset and demo concept. Chris L. Santo (Scottsdale Community College) guided the Python/GitHub/Streamlit exercise during NITIC Summer Working Connections in June 2026. Additional visualization experiments, including the animated heat map, were developed by Professor Brian Daily using AI assistance.
Student-selected datasets
The starter package includes a `sample_datasets` folder with three fictional accounting CSVs and a short README. Students can choose one, copy it beside `streamlit_app.py` in a new GitHub repository, and use AI to create a separate dashboard appropriate for that dataset. They do not need to use the Uber map with an accounting CSV. The Canvas optional lesson also links to other public sample datasets; check source usage rights.
