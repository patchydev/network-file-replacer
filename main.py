import random
from mitmproxy import http

with open("linus.jpg", "rb") as f:
    chosen_image_data = f.read()

precomputed_headers = {
    "Content-Type": "image/jpeg",
    "Content-Length": str(len(chosen_image_data))
}

class RandomImageReplacer:
    __slots__ = ["prob"]
    
    def __init__(self, replacement_probability=1.0):
        self.prob = replacement_probability

    def response(self, flow: http.HTTPFlow):
        ctype = flow.response.headers.get("Content-Type", "")
        if ctype.startswith("image/"):
            if random.random() < self.prob:
                flow.response.content = chosen_image_data
                flow.response.headers.clear()
                for k, v in precomputed_headers.items():
                    flow.response.headers[k] = v

addons = [RandomImageReplacer(replacement_probability=0.25)]
