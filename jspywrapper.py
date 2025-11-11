from core import lib
from ctypes import c_int, c_bool, c_void_p, c_char_p

def executeJavaScript(surface_id: int, script: str):
    """
    Executes JavaScript code in the context of the web surface identified by surface_id.
    """
    if not isinstance(script, str):
        raise ValueError("Script must be a string.")
    
    # Convert the Python string to a C-style string (bytes)
    script_c = c_char_p(script.encode('utf-8'))
    
    # Call the C++ function to execute the script
    result = lib.evaluateScript(c_int(surface_id), script_c)
    
    return result

def checkJsSyntax(surface_id: int, script: str) -> bool:
    """
    Checks the syntax of the provided JavaScript code without executing it.
    Returns True if the syntax is correct, False otherwise.
    """
    if not isinstance(script, str):
        raise ValueError("Script must be a string.")
    
    # Convert the Python string to a C-style string (bytes)
    script_c = c_char_p(script.encode('utf-8'))
    
    # Call the C++ function to check the syntax
    is_valid = lib.checkJSSyntax(c_int(surface_id), script_c)
    
    return bool(is_valid)