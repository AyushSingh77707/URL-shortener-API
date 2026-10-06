import string

CHARACTERS= string.ascii_letters + string.digits    

def base62_encoding(num:int):
    num= num + 100_000_000
    result=[]
    while num:
        result.append(CHARACTERS[num%2])
        num//=62
    return ''.join(reversed(result)) or CHARACTERS[0]

