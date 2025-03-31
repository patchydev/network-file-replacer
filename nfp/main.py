import os
import random
import ctypes
from mitmproxy import http
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(script_dir, "target", "release", "libnfp.so")

if not os.path.exists(lib_path):
    lib_path = os.path.join(script_dir, "target", "release", "nfp.dll")

if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Rust library not found at {lib_path}. Please build it first.")

rust_lib = ctypes.CDLL(lib_path)

rust_lib.should_replace.argtypes = [ctypes.c_double]
rust_lib.should_replace.restype = ctypes.c_bool

rust_lib.get_image_data.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
rust_lib.get_image_data.restype = ctypes.POINTER(ctypes.c_ubyte)

rust_lib.free_image_data.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
rust_lib.free_image_data.restype = None

class ImageCache:
    def __init__(self):
        self.image_data = None
        self.content_type = "image/jpeg"

    def load_image(self, image_path):
        image_path_bytes = image_path.encode('utf-8')
        size = ctypes.c_size_t()
        ptr = rust_lib.get_image_data(image_path_bytes, ctypes.byref(size))

        if not ptr:
            return None

        buffer_size = size.value

        python_bytes = bytes(ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte * buffer_size)).contents)

        rust_lib.free_image_data(ptr)

        self.image_data = python_bytes

        ext = os.path.splitext(image_path)[1].lower()
        if ext == '.png':
            self.content_type = 'image/png'
        elif ext == '.gif':
            self.content_type = 'image/gif'
        elif ext == '.webp':
            self.content_type = 'image/webp'
        else:
            self.content_type = 'image/jpeg'

        return self.image_data

class ImageReplacer:
    def __init__(self, replacement_probability=0.25):
        self.prob = replacement_probability
        self.image_path = os.path.join(script_dir, "linus.jpg")
        self.cache = ImageCache()

        self.load_image()

    def load_image(self):
        image_data = self.cache.load_image(self.image_path)
        if not image_data:
            print("Failed to load image!")

    def response(self, flow: http.HTTPFlow):
        if not flow.response or not flow.response.headers.get("content-type", "").startswith("image/"):
            return

        if rust_lib.should_replace(self.prob):
            if not self.cache.image_data:
                self.load_image()
                if not self.cache.image_data:
                    return

            flow.response.content = self.cache.image_data
            flow.response.headers["content-type"] = self.cache.content_type
            flow.response.headers["content-length"] = str(len(self.cache.image_data))

addons = [ImageReplacer(replacement_probability=0.50)]