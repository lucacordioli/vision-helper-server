from langchain_core.tools import tool

from src.utils import shared_data
from src.utils.functions import get_id_from_text, get_info_from_id


@tool
def find_element(query: str):
    """Call if you want to highlight an element by its ID"""
    print("find_element")

    json_data = shared_data.get_json_data()
    ids = get_id_from_text(query, json_data)
    return {"messages": ids[0], "item_id": ids[0]}

    # if "engine" in query.lower():
    #     return {"messages": "45", "item_id": "45"}
    # return {"messages": "01", "item_id": "01"}


@tool
def get_info(element_id: str):
    """Call if you have the element id and need to find textual, explanation information related to it."""
    print("get_info")

    json_data = shared_data.get_json_data()
    res = get_info_from_id(element_id, json_data)
    return {"messages": res["text"], "page_n": res["page_n"],
            "pdf": res["document_id"]}  # if necessary, change the pdf_name

    # if "01" in element_id.lower():
    #     return {"messages": "Engine 1 is a powerful engine that can generate 1000 horsepower."}
    # return {"messages": "shit."}
