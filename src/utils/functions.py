from src.utils.knowledge import Knowledge

knowledge = Knowledge()


def get_info_from_id(obj_id: int, json_data: object) -> dict:
    """
    Get information from the id of the elements
    :param obj_id: the id of the element
    :param json_data: the json data to search in
    :return: page number and explanation
    """

    obj = None
    for media in json_data['medias']:
        if media["id"] == obj_id:
            obj = media

    if obj is None:
        return {"error": "Element not found"}

    item_id = obj['id']
    name = obj['name']
    caption = obj['caption']
    guid = obj['guid']
    media_type = obj['mediaType']['value']

    query_text = f"ID: {item_id}, Name: {name}, Caption: {caption}, GUID: {guid}, MediaType: {media_type}"

    res = knowledge.query(query_text)

    page_number = str(res["metadatas"][0][0]["page"])
    text = res["documents"][0][0]

    return {"page_number": page_number, "text": text}


def get_id_from_text(text: str, json_data: object) -> [int]:
    """
    Get information from the text of the elements
    :param text: the text of the element
    :param json_data: the json data to search in
    :return: obj_id
    """

    knowledge.create_elements_collection(json_data['medias'])
    res = knowledge.query(text)

    context = ""
    for doc in res["documents"]:
        context += "\n\n".join(doc)

    print(res["documents"][0][0])

    prompt_embedding = text + "\n\n" + res["documents"][0][0]
    print(prompt_embedding)


    res = knowledge.query_elements_collection(prompt_embedding)

    ids = []

    for id_list in res['ids']:
        for item in id_list:
            id_value = int(item.split('_')[1])
            ids.append(id_value)

    return ids








