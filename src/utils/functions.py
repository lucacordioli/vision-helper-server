import json
import re

from src.utils.knowledge import Knowledge

knowledge = Knowledge()


def get_info_from_id(obj_id: str, json_data: object) -> dict:
    """
    Get information from the id of the elements
    :param obj_id: the id of the element
    :param json_data: the json data to search in
    :return: page number and explanation
    """
    obj = None
    for task in json_data.get('deckTasks', []):
        for step in task.get('steps', []):
            for node in step.get('listOfNode3D', []):
                # Extract node details without elements
                if node['id'] == obj_id:
                    obj = node

                # Extract elements from node
                for element in node.get('listOfElement3D', []):
                    if element['id'] == obj_id:
                        obj = element

    if obj is None:
        return {"error": "Element not found"}

    item_id = obj['id']
    name = obj['name']
    if 'caption' in obj:
        caption = obj['caption']
    else:
        caption = ""

    query_text = f"ID: {item_id}, Name: {name}, Caption: {caption}"

    res = knowledge.query(query_text)

    page_number = str(res["metadatas"][0][0]["page"])
    text = res["documents"][0][0]

    return {"page_n": page_number, "text": text}


def get_id_from_text(text: str, json_data) -> [str]:
    """
    Get information from the text of the elements
    :param text: the text of the element
    :param json_data: the json data to search in
    :return: obj_id
    """

    nodes = []
    elements = []

    for task in json_data.get('deckTasks', []):
        for step in task.get('steps', []):
            for node in step.get('listOfNode3D', []):
                # Extract node details without elements
                node_copy = node.copy()
                node_copy.pop('listOfElement3D', None)
                node_copy['type'] = 'node'
                nodes.append(node_copy)

                # Extract elements from node
                for element in node.get('listOfElement3D', []):
                    elements.append(element)

    knowledge.create_elements_collection(nodes + elements)
    res = knowledge.query(text)

    context = ""
    for doc in res["documents"]:
        context += "\n\n".join(doc)

    prompt_embedding = text + "\n\n" + res["documents"][0][0]

    res = knowledge.query_elements_collection(prompt_embedding)

    ids = []
    for doc_list in res['documents']:
        for str_item in doc_list:
            json_str = re.sub(r"(?<!\\)'", '"', str_item)
            json_str = json_str.replace("True", "true").replace("False", "false").replace("None", "null")
            item = json.loads(json_str)
            id_value = item['id']
            if item['type'] == 'node':
                type = 'node'
            else:
                type = 'element'
            ids.append({'id': id_value, 'type': type})
    return ids
