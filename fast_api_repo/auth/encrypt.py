import hashlib

def encrypt_by_md5(salt:str,value:str)->str:
    md5_obj = hashlib.md5()  
    md5_obj.update((value + salt).encode("utf-8"))  
    return md5_obj.hexdigest()  