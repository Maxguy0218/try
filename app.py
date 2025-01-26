import streamlit as st
import pandas as pd
import re
import pdfplumber

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract and classify clauses
def split_into_paragraphs(text):
    # Split text into paragraphs based on line breaks
    paragraphs = text.split("\n")
    paragraphs = [para.strip() for para in paragraphs if para.strip()]  # Remove empty lines
    return paragraphs

def extract_and_classify_clauses(text):
    # Define clause patterns and associated business areas
    patterns = {
        "Care Contingency / Patient Care Safeguard": {
            "pattern": r"(continuity of care|patient care)",
            "business_area": "Operational Risk Management",
        },
        "Contract Administration / Notices": {
            "pattern": r"(policy updates|emergency admission|changes to required documentation)",
            "business_area": "Operational Risk Management",
        },
        "Revenue Cycle Management": {
            "pattern": r"(requests for additional information|overpayment recovery|claim denial resolution)",
            "business_area": "Financial Risk Management",
        },
        "Billing and Collection": {
            "pattern": r"(prohibited billing practices|false claims|billing compliance)",
            "business_area": "Financial Risk Management",
        },
        "Contract Termination": {
            "pattern": r"(termination notice|termination process)",
            "business_area": "Operational Risk Management",
        },
    }

    clauses = []
    paragraphs = split_into_paragraphs(text)  # Split the document into paragraphs

    for para in paragraphs:
        for category, details in patterns.items():
            # Match patterns in each paragraph
            if re.search(details["pattern"], para, flags=re.IGNORECASE):
                clauses.append({
                    "Obligation Type": category,
                    "Description": para.strip(),  # Use the entire paragraph as the clause
                    "Business Area": details["business_area"],
                })

    return clauses


# Function to create a structured table
def create_table(clauses):
    return pd.DataFrame(clauses)

# Streamlit app
st.title("Document Clause Extractor")
st.write("Upload a PDF document to extract and generate a structured table with full clauses in the **Description** column.")

# File upload
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    # Extract text from PDF
    st.write("Processing PDF document...")
    document_text = extract_text_from_pdf(uploaded_file)

    # Display extracted text (optional for debugging)
    if st.checkbox("Show extracted text"):
        st.write(document_text)

    # Extract and classify clauses
    st.write("Extracting and classifying clauses...")
    classified_clauses = extract_and_classify_clauses(document_text)

    # Generate the table
    if classified_clauses:
        table = create_table(classified_clauses)
        st.write("Generated Table:")
        st.table(table)  # Display table on the page

        # Downloadable CSV
        csv = table.to_csv(index=False)
        st.download_button(
            label="Download Table as CSV",
            data=csv,
            file_name="extracted_clauses.csv",
            mime="text/csv"
        )
    else:
        st.warning("No clauses matched the predefined patterns. Try refining your document.")
