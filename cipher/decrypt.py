from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# key =

with open('../config', 'rb') as c_file:
    iv = c_file.read(16)
    cipher_text = c_file.read()

cipher = AES.new(key, AES.MODE_CBC, iv)

plain_text = unpad(cipher.decrypt(cipher_text), AES.block_size)

with open('../config.ini', 'wb') as c_file:
    c_file.write(plain_text)
