import zlib


def unordered(file_path):
    """
    Generates a hash of a file, not impacted by line order.
    Not anywhere near cryptographically secure.
    """
    file_hash = 1
    eighth_mersenne_prime = 2147483647
    with open(file_path) as file:
        print("Hashing", file_path)
        for line in file:
            file_hash = (zlib.adler32(line.encode()) * file_hash) % eighth_mersenne_prime
    print("Hash is", file_hash)
    return file_hash
