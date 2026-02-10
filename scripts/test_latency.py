
import requests
import time
import json

TEXT = "This is a very long text that we want to synthesize. " * 20  # ~200 words
URL = "http://localhost:9090/synthesize"

print(f"Sending request with {len(TEXT)} characters...")
start_time = time.time()
try:
    response = requests.post(URL, json={"text": TEXT}, stream=True)
    if response.status_code == 200:
        # Read the first chunk to measure Time to First Byte (TTFB) effectively 
        # (though for non-streaming response, it waits for full generation)
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                break
        ttfb = time.time() - start_time
        print(f"Time to First Chunk: {ttfb:.4f}s")
        
        # Read the rest
        content_size = 0
        for chunk in response.iter_content(chunk_size=1024):
            content_size += len(chunk)
        
        total_time = time.time() - start_time
        print(f"Total Time: {total_time:.4f}s")
        print(f"Content Size: {content_size} bytes")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
