import subprocess
import time
import requests
import psutil
import os
import signal

BATCH_SIZES = [2, 4, 8]
# Max chunk is 300 chars.
# Batch 8 needs ~2400 chars to be full.
# Let's use ~2500 chars to cover it.
TEXT = "This is a very long text that we want to synthesize. " * 50
URL = "http://localhost:9090/synthesize"
LOG_FILE = "/tmp/chichi_benchmark.log"

def start_server(batch_size):
    print(f"Starting server with BATCH_SIZE={batch_size}...")
    # We use a modified start command to pass the env var
    # We can't easily use start_server.sh because we need to inject BATCH_SIZE
    # But start_server.sh doesn't take generic env vars easily unless we export them before calling it.
    # Actually, if we export BATCH_SIZE before calling start_server.sh, it *might* be picked up 
    # if start_server.sh doesn't scrub env or if we modify it to pass it through.
    # Looking at start_server.sh, it runs:
    #   nohup bash -c "export UV_PROJECT_ENVIRONMENT=...; ... uv run uvicorn ..."
    # It sets UV_PROJECT_ENVIRONMENT inside the bash -c string, but inherits other env vars from the parent shell?
    # Yes, typically variables exported in the shell calling nohup are available to the command inside.
    
    # Let's try setting the env var and calling start_server.sh
    env = os.environ.copy()
    env["BATCH_SIZE"] = str(batch_size)
    
    # Ensure any previous server is stopped
    subprocess.run(["./scripts/stop_server.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # Start server
    subprocess.run(["./scripts/start_server.sh"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for startup
    print("Waiting for server startup...")
    for _ in range(60):
        try:
            resp = requests.get("http://localhost:9090/docs")
            if resp.status_code == 200:
                print("Server is ready.")
                return
        except:
            time.sleep(1)
    
    raise Exception("Server failed to start")

def get_server_process():
    # Find the python process running uvicorn
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'uvicorn' in ' '.join(cmdline) and 'chichi_speech.server:app' in ' '.join(cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def monitor_memory(proc, stop_event, max_mem_container):
    while not stop_event.is_set():
        try:
            mem = proc.memory_info().rss / 1024 / 1024  # MB
            if mem > max_mem_container[0]:
                max_mem_container[0] = mem
            time.sleep(0.1)
        except:
            break

def benchmark(batch_size):
    start_server(batch_size)
    
    # Let it settle
    time.sleep(2)
    
    proc = get_server_process()
    if not proc:
        print("Could not find server process to monitor memory.")
        return None
        
    print(f"Monitoring process {proc.pid}...")
    
    # Memory monitoring
    max_mem = [0]
    import threading
    stop_event = threading.Event()
    mem_thread = threading.Thread(target=monitor_memory, args=(proc, stop_event, max_mem))
    mem_thread.start()
    
    # Run request
    print("Sending request...")
    start_time = time.time()
    try:
        response = requests.post(URL, json={"text": TEXT})
        if response.status_code != 200:
            print(f"Request failed: {response.status_code}")
    except Exception as e:
        print(f"Request error: {e}")
        
    latency = time.time() - start_time
    print(f"Latency: {latency:.2f}s")
    
    stop_event.set()
    mem_thread.join()
    
    print(f"Peak Memory: {max_mem[0]:.2f} MB")
    
    return latency, max_mem[0]

def main():
    results = []
    print(f"Benchmarking Batch Sizes: {BATCH_SIZES}")
    
    for bs in BATCH_SIZES:
        print(f"\n--- Batch Size: {bs} ---")
        try:
            lat, mem = benchmark(bs)
            results.append((bs, lat, mem))
        except Exception as e:
            print(f"Failed benchmark for {bs}: {e}")
            
    print("\n\n=== Results ===")
    print(f"{'Batch Size':<12} | {'Latency (s)':<12} | {'Memory (MB)':<12}")
    print("-" * 42)
    for bs, lat, mem in results:
        print(f"{bs:<12} | {lat:<12.2f} | {mem:<12.2f}")

if __name__ == "__main__":
    main()
