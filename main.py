import requests
import customtkinter
import keyboard
import time
import clipboard
import os

from item import Item
from bs4 import BeautifulSoup

### Built with customTKInter ### 
### https://github.com/TomSchimansky/CustomTkinter ###

def index_uniques():
    if (login_frame.remember_me_check_box.get() == 1):
        store_login_info()
    else:
        clear_login_info()

    username = login_frame.username_input.get()
    session_ID = login_frame.session_ID_input.get()
    tabs = []

    headers = {'user-agent': username}
    cookies = {'POESESSID': session_ID}

    # Get stash ID corresponding to user name
    stashes = requests.get(f"https://www.pathofexile.com/account/view-profile/{username}/stashes", headers=headers, cookies=cookies)
    if (stashes.status_code == 200):
        stash_ID = stashes.text.split("view-stash/"+username+"/")[1].split()[0]
        stash_ID = ''.join(c for c in stash_ID if c.isalnum())
    else:
        status.configure(text="Invalid account name or session ID. Error Code: "+str(stashes.status_code))
        return
    
    # Access and index the stash tab that containins the collection
    collection = requests.get(f"https://www.pathofexile.com/account/view-stash/{username}/{stash_ID}/", headers=headers, cookies=cookies)
    if (collection.status_code == 200):
        status.configure(text="Indexing your collection...")
        login_frame.forget()
        progress_bar_frame = IndexingProgressFrame(master=root)
        progress_bar_frame.pack(pady=20, padx=60, fill="both", expand=False)
        progress_bar_frame.progress_bar.set(0)
        root.update()
    else:
        status.configure(text="Invalid account name or session ID. Error Code: "+str(collection.status_code))
        return

    for i in range(22):
        tabs.append(f"https://www.pathofexile.com/account/view-stash/{username}/5e340320/{i+1}")

    for i, tab in enumerate(tabs):
        progress_bar_frame.progress_bar.set(i/21)
        root.update()

        response = requests.get(tab, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.content, "html.parser")

        for item in soup.find_all("div", {"class": "item owned"}):
            owned_items.append(item.text.strip())

        for item in soup.find_all("div", {"class": "item unowned"}):
            unowned_items.append(item.text.strip())

    # Indexing finished succesfully
    progress_bar_frame.forget()
    status.configure(text=f"Done indexing. Your collection is { round(len(owned_items) / (len(unowned_items) + len(owned_items)), 4) * 100}% complete.\nPress CTRL+C while hovering over an item to look for it in your collection.")

# Compare item data in clipboard to collection
def check_item_in_clipboard():
        # Make sure the clipboard has time to update
        time.sleep(0.25)
        # PoE item data always contains the string "--------", so we use that to make sure the clipboard contains an item
        if ("--------" in clipboard.paste()):
            item = Item(clipboard.paste())
            if (item.is_unique()):
                if (owned_items.__contains__(item.name)):
                    status.configure(text=f"You already have {item.name} in your collection.")
                else:
                    status.configure(text=f"Congratiulations, {item.name} is a new unique!")
            else:
                status.configure(text=f"{item.name} is not unique")

def store_login_info():
    f = open("LoginInfo", "w")
    f.writelines([login_frame.username_input.get() + "\n", login_frame.session_ID_input.get() + "\n", str(login_frame.remember_me_check_box.get())])

def get_login_info():
    try:
        with open("LoginInfo") as f:
            info = f.readlines()
            login_frame.username_input.insert(0, info[0].rstrip())
            login_frame.session_ID_input.insert(0, info[1].rstrip())
            if (info[2] == "1"):
                login_frame.remember_me_check_box.select()
    except:
        pass

def clear_login_info():
    try:
        os.remove("LoginInfo")
    except OSError:
        pass

### UI ###

class LoginFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username_input = customtkinter.CTkEntry(self, placeholder_text="Username")
        self.username_input.pack(pady=12, padx=10)

        self.session_ID_input = customtkinter.CTkEntry(self, placeholder_text="SessionID")
        self.session_ID_input.pack(pady=12, padx=10)

        self.index_uniques_button = customtkinter.CTkButton(self, text="Index Uniques", command=index_uniques)
        self.index_uniques_button.pack(pady=12, padx=10)

        self.remember_me_check_box = customtkinter.CTkCheckBox(self, text="Remember Me")
        self.remember_me_check_box.pack(pady=12, padx=10)

class IndexingProgressFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="ProgresssBarFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.header = customtkinter.CTkLabel(self, text=self.header_name)

        self.progress_bar = customtkinter.CTkProgressBar(self)
        self.progress_bar.pack(padx=12, pady=10)

if __name__ == "__main__":

    def close():
        global running;
        running = False

    running = True
    owned_items = []
    unowned_items = []

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("green")

    root = customtkinter.CTk()
    root.geometry("440x280")
    root.resizable(False, False)
    root.title("Unique Tracker")
    root.protocol("WM_DELETE_WINDOW", close)

    login_frame = LoginFrame(master=root)
    login_frame.pack(pady=20, padx=60, fill="both", expand=False)

    status = customtkinter.CTkLabel(master=root, text="")
    status.pack(pady=12, padx=10)

    get_login_info()

    while running:
        root.update()
        if keyboard.is_pressed("ctrl+c"):
            check_item_in_clipboard()
    
    root.destroy()
