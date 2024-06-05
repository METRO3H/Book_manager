def color(color, message):
    if color == "white":
        return f"\033[97m{message}\033[0m"
    
    if color == "magneta":
        return f"\033[95m{message}\033[0m"
    
    if color == "green":
        return f"\033[32m{message}\033[0m"
    
    if color == "yellow":
        return f"\033[93m{message}\033[0m"
    
    if color == "blue":
        return f"\033[94m{message}\033[0m"
    
    if color == "grey":
        return f"\033[90m{message}\033[0m"
    if color == "cyan":
        return f"\033[36m{message}\033[0m"
    else:
        return "errorXD"