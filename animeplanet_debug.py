import tls_client
import time

url = "https://www.anime-planet.com/anime/top-anime"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none'
}

print("Starting request with tls-client, retry logic and rate limiting...")

# Add initial delay to avoid immediate blocking
time.sleep(2)

# Create TLS client session
session = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True
)

# Try multiple times with increasing delays
for attempt in range(3):
    try:
        print(f"Attempt {attempt + 1}/3...")
        
        response = session.get(url, headers=headers, timeout_seconds=30)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Got status code 200")
            print(f"Response length: {len(response.text)} characters")
            print(f"Content preview: {response.text[:200]}...")
            break
        elif response.status_code == 403:
            print(f"❌ Attempt {attempt + 1}: Got 403 Forbidden")
            if attempt < 2:  # Not the last attempt
                wait_time = 5 * (attempt + 1)
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("All attempts failed. AnimePlanet may be blocking requests.")
        else:
            print(f"❌ Got unexpected status code: {response.status_code}")
            print(f"Response text preview: {response.text[:200]}...")
            break
            
    except Exception as e:
        print(f"❌ Request failed on attempt {attempt + 1}: {e}")
        if attempt < 2:
            print(f"Waiting 5 seconds before retry...")
            time.sleep(5)
        else:
            print("All attempts failed due to errors.")

# Close the session
session.close()
