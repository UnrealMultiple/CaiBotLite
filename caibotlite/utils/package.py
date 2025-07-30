import base64
import gzip
import io


def decompress_base64_gzip(base64_string):
    compressed_data = base64.b64decode(base64_string)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gzip_file:
        decompressed_data = gzip_file.read()

    return decompressed_data.decode('utf-8')
