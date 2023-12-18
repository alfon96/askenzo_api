from fastapi import FastAPI
from api_routers.tourist_api import tourist
from api_routers.host_api import host
from api_routers.discovery_api import discovery
from api_routers.experiences_api import experience
from api_routers.admin_api import admin
from api_routers.popup_msg import popup
from api_routers.image_api import image
from fastapi.middleware.cors import CORSMiddleware


description = """
## 🧳Tourist APIs
* **Get**: get the single user instance, with all its fields.\n
* **Update**: update every field at once, it doesn't update new empty fields (no pass).\n
* **Update Password**: update tourist's password.\n
* **Signup**: creates a new tourist.\n
* **Delete**: delete tourist.\n
* **Get Likes**: get all user's liked experiences by id.\n
* **Toggle Likes**: creates(deletes) a new(existing) like.\n
* **Signin**: signin function.\n

## 🏨 Host APIs
* **Get**: get the single host instance, with all its fields.\n
* **Update**: update every field at once, it doesn't update new empty fields (no pass).\n
* **Update Password**: update tourist password.\n
* **Signup**: creates a new host.\n
* **Delete**: delete the host by its id.\n
* **Signin**: login function.\n

## 🚣 Experience
* **Get**: get a list of N experiences by id, from cursor x.\n
* **Update**: update every field at once, it doesn't update new empty fields.\n
* **Create**: creates a new experience.\n
* **Delete**: delete the experience by its id.\n

## 🏛️ Discovery
* **Get**: get a list of N discovery, from x to y.\n
* **Update**: update every field at once, it doesn't update new empty fields.\n
* **Create**: creates a new discovery.\n
* **Delete**: delete the discovery by its id.\n

## 💬 Popup
* **Get**: get a list of N popups, from x to y.\n
* **Update**: update every field at once, it doesn't update new empty fields.\n
* **Create**: creates a new popup.\n
* **Delete**: delete the popup by its id.\n

## 🖼️ Images
* **Update**: replace an existing image.\n
* **Create**: creates a new image.\n
* **Delete**: delete an image by its link.\n

## 💂Admin
* **Login**: login function.\n
"""

# Set-ExecutionPolicy Unrestricted -Scope Process
app = FastAPI(title="🚀 AskEnzo API", description=description, version="1.0.1")

@app.get("/")
def home(): return {"message": "Benvenuto nelle API"}

def main():
    """
    The main function sets up a FastAPI application with various routers and middleware for handling
    different API endpoints.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(tourist)
    app.include_router(host)
    app.include_router(experience)
    app.include_router(discovery)
    app.include_router(image)
    app.include_router(admin)
    app.include_router(popup)
    
    

if __name__=='main':
    main()
