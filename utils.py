def print_request_body(data: dict) -> None:
    """ print request body
    """
    data_to_print = dict()
    for key, value in data.items():
        if 'password' == key:
            pass
        
        else:
            data_to_print[key] = value
    
    print(data_to_print)