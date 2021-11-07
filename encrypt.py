from cryptography.fernet import Fernet
import os

def write_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()


def decrypt(filename, key):
    """
    Given a filename (str) and key (bytes), it decrypts the file and write it
    """
    output_file = os.path.splitext(filename)[0] + "_decrypted" + ".flac"
    input_file = os.path.splitext(filename)[0] + ".encrypted"
    f = Fernet(key)
    with open(input_file, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    # write the original file
    with open(output_file, "wb") as file:
        file.write(decrypted_data)

def encrypt(filename, key, data):
    """
    Given a filename (str) and key (bytes), it encrypts the file and write it
    """
    output_file = os.path.splitext(filename)[0] + ".encrypted"
    f = Fernet(key)
    '''with open(filename, "rb") as file:
        # read all file data
        file_data = file.read()'''
    # encrypt data
    encrypted_data = f.encrypt(data)
     # write the encrypted file
    with open(output_file, "ab") as file:
        file.write(encrypted_data)

if not os.path.exists("key.key"):
    write_key()

if __name__ == "__main__":
    #write_key()

    key = load_key()
    filename = input("filename>")
    try:
        encrypt(filename, key)
    except:
        pass
    try:
        decrypt(filename, key)
    except Exception as e:
        print(e)
