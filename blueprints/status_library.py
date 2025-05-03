def status_success(message : str, data = None):
    response = {
        "status" : "success",
        "message" : message
    }
    if data is not None:
        response["data"] = data
    return response

def status_error(message : str, data = None):
    return {
        "status" : "error",
        "message" : message,
        (data is not None) and "data" : data
    }