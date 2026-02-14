# здесь будут дополнительные штуки для украшения или оформления вывода,
# использоваться они будут в services.basic

async def create_output(list_task:list[dict]) -> list[list]:

    res = []

    for task in list_task:
        res.append([
        task["id"],
        task["name"],
        task["created_at"],
        task["deadline"],
        task["priority"],
        task["note"],
        task["completed"]
    ])

    return res