def status_success(message : str, data = None):
    response = {
        "status" : "success",
        "message" : message
    }
    if data is not None:
        response["data"] = data
    return response

def status_error(message : str):
    return {
        "status" : "error",
        "message" : message
    }