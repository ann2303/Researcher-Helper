from typing import Any

from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

pdf_prompt_text = """You are an assistant tasked with summarizing tables and text. \ 
    Give a concise summary of the table or text. Table or text chunk: {element} """
pdf_prompt = ChatPromptTemplate.from_template(pdf_prompt_text)


class Element(BaseModel):
    type: str
    text: Any


def generate_pdf_summary(pdf_path: str, outputdir, openai_api_key: str) -> Any:
    """
    Generate a summary of the PDF at the given path.
    """
    # Load the PDF
    pdf_text = partition_pdf(pdf_path)
    # Get elements
    raw_pdf_elements = partition_pdf(
        filename=pdf_path,
        extract_images_in_pdf=False,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=pdf_path,
    )
    # Categorize by type
    categorized_elements = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            categorized_elements.append(Element(type="table", text=str(element)))
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            categorized_elements.append(Element(type="text", text=str(element)))

    # Tables
    table_elements = [e for e in categorized_elements if e.type == "table"]

    # Text
    text_elements = [e for e in categorized_elements if e.type == "text"]
    # Prompt

    # Summary chain
    model = ChatOpenAI(temperature=0, model="gpt-4", openai_api_key=openai_api_key)
    summarize_chain = {"element": lambda x: x} | pdf_prompt | model | StrOutputParser()
    # Apply to tables
    tables = [i.text for i in table_elements]
    table_summaries = summarize_chain.batch(tables, {"max_concurrency": 5})
    # Apply to texts
    texts = [i.text for i in text_elements]
    text_summaries = summarize_chain.batch(texts, {"max_concurrency": 5})
    return {"tables": table_summaries, "texts": text_summaries}