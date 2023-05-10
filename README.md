# LocalIPAStore
Not to be confused with LocalIAPStore

## What is this?
A dumb, simple PlayCover-compatible decryption server for app packages

## How do I use this?
1. Install the dependencies: `pip3 install -r requirements.txt`
2. Install additional dependencies: 
- ideviceinstaller
- libimobiledevice

3. Run the server: `python3 src/main.py`

## How do I use this with PlayCover?
1. Install PlayCover from [here](https://playcover.io)
2. Add your source to PlayCover (default is `http://localhost:8000/library`)

## Docs?
API endpoints are generated by FastAPI as OpenAPI 3.0 in `/docs`