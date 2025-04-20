def status_success(message : str):
    return {
        "status" : "success",
        "message" : message
    }

def status_error(message : str):
    return {
        "status" : "error",
        "message" : message
    }