import hashlib


def psw_Encrypt(text):
    md5_obj = hashlib.md5()
    b = text.encode(encoding='UTF-8')
    md5_obj.update(b)
    str_md5 = md5_obj.hexdigest()
    return str_md5
