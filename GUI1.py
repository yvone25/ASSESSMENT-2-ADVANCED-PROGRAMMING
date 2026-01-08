from tkinter import * # Tkinter library to create the GUI windows
import urllib.request # For making HTTP requests to APIs
import json # To handle JSON data from the API
from PIL import Image, ImageTk # Pillow library to import and display images from the API
from io import BytesIO # To convert image data from URL to a file-like object for PIL

root = Tk() # Create the main Tkinter window object
root.title("Country Explorer with Flags")
root.geometry("600x900") # Set window size to 600x900 pixels
root.config(bg="#9dc183")  # Set background color to sage green (#9dc183)

# Global variables to store countries data and flag images
countriesdata = [] # Global list to store countries data for access throughout the code
current_flag_image = None # To keep reference to the current flag image and prevent garbage collection

def search(): 
    """Searches for countries when connected to the search button"""
    countryname = entry.get() # Get text input from the entry field
    if countryname == "": # Validate input - if empty, show error message
        resultl.config(text="Please enter a country name", fg="#3e4d34")
        return 

    try:
        # Make request to the REST Countries API with the country name
        url = f"https://restcountries.com/v3.1/name/{countryname}"
        response = urllib.request.urlopen(url)  # Send GET request to the API
        data = json.loads(response.read().decode()) # Convert JSON response to Python dictionary
        
        global countriesdata  # Access the global countriesdata variable
        countriesdata = data

        if not countriesdata:  # If no country is found, clear display and show message
            resultl.config(text="No country found", fg="#3e4d34")
            flag_label.config(image='')   # Clear the flag image
            flag_label.config(text="")   # Clear the flag text
            instructions.delete("1.0", END)  # Clear instructions Text widget
            countrylist.delete("1.0", END)  # Clear country Text widget
            listbox.delete(0, END) # Clear Listbox
            return
        
        # Fill Listbox with country names if multiple countries are returned
        listbox.delete(0, END)  # Clear existing Listbox entries
        for country in countriesdata:
            listbox.insert(END, country["name"]["common"])
        showcountry(0) # Display the first country by default

    except urllib.error.HTTPError:
        resultl.config(text="Error getting country data", fg="#3e4d34")
    except Exception as e:   # If API request fails, show error message
        resultl.config(text=f"Error: {str(e)}", fg="#3e4d34")

def showcountry(index):
    """Display country details (name, info, flag) at the given index."""
    if not countriesdata or index >= len(countriesdata):
        return
        
    country = countriesdata[index]  # Get country from the global list by index
    
    # Display country name
    common_name = country["name"]["common"]
    official_name = country["name"]["official"]
    resultl.config(text=f"{common_name} ({official_name})", fg="#000000")
    
    # Display country information in instructions area
    instructions.delete("1.0", END)   # Clear previous instructions to prevent overlap
    
    info_text = ""
    if 'capital' in country:
        info_text += f"Capital: {', '.join(country['capital'])}\n"
    
    if 'region' in country:
        info_text += f"Region: {country['region']}\n"
    
    if 'population' in country:
        info_text += f"Population: {country['population']:,}\n"  # Format with commas
    
    if 'area' in country:
        info_text += f"Area: {country['area']:,} km²\n"  # Format with commas
    
    if 'languages' in country:
        languages = ', '.join(country['languages'].values())
        info_text += f"languages: {languages}\n"
    
    if 'currencies' in country:
        currencies = []
        for code, currency_info in country['currencies'].items():
            currencies.append(f"{currency_info['name']} ({currency_info['symbol']})")
        info_text += f"Currency: {', '.join(currencies)}\n"
    
    if 'timezones' in country:
        info_text += f"Timezones: {', '.join(country['timezones'])}\n"
    
    instructions.insert(END, info_text)  # Insert new instructions into text widget
    
    # Display country details in country area
    countrylist.delete("1.0", END)  # Clear previous country details to prevent overlapping
    country_details = [] # Create a list to store additional country information
    
    if 'subregion' in country:
        country_details.append(f"Subregion: {country['subregion']}")
    
    if 'tld' in country:
        country_details.append(f"Domain: {', '.join(country['tld'])}")
    
    if 'idd' in country and 'root' in country['idd']:
        root_code = country['idd']['root']
        suffixes = country['idd'].get('suffixes', [''])[0] if 'suffixes' in country['idd'] else ''
        country_details.append(f"Calling Code: {root_code}{suffixes}")
    
    if 'car' in country and 'side' in country['car']:
        country_details.append(f"Drives on: {country['car']['side']} side")
    
    if 'startOfWeek' in country:
        country_details.append(f"Start of week: {country['startOfWeek']}")
    
    countrylist.insert(END, "\n".join(country_details))  # Display in Text widget
    
    # Display country flag as IMAGE
    if 'flags' in country and 'png' in country['flags']:
        flag_url = country["flags"]["png"] # Get URL of country flag from the API data
        try:
            # Download and display the flag image
            with urllib.request.urlopen(flag_url) as response:
                img_data = response.read() # Download image data as bytes
            
            # Convert image data to PIL Image using BytesIO
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 120)) # Resize image to fit GUI dimensions
            
            # Convert PIL image to Tkinter-compatible image
            global current_flag_image # Access global variable
            current_flag_image = ImageTk.PhotoImage(img)
            
            # Set image label to the new photo
            flag_label.config(image=current_flag_image)
            flag_label.image = current_flag_image  # Keep reference to avoid garbage collection
            
        except Exception as e:
            flag_label.config(image='', text=f"Flag load error") # Show error if image fails to load
    else:
        flag_label.config(image='', text="No flag available") # Show placeholder if no flag exists

def select(event):
    """Handle user selection from the Listbox and show country details"""
    if listbox.curselection():   # Check if a selection exists in the listbox
        index = listbox.curselection()[0]  # Get the index of the selected country
        showcountry(index)  

def searchbyregion():
    """Search countries by region - displays all countries in the specified region"""
    region = region_entry.get() # Get region name from Entry widget
    if region == "": # Ensure user enters a valid region
        resultl.config(text="Please enter a region", fg="#3e4d34")
        return
    
    try:
        # Request countries from the region API endpoint
        url = f"https://restcountries.com/v3.1/region/{region}"
        response = urllib.request.urlopen(url) 
        
        if response:
            global countriesdata
            countriesdata = json.loads(response.read().decode()) # Convert JSON response to Python dict
            
            if countriesdata:
                listbox.delete(0, END)
                for country in countriesdata:
                    listbox.insert(END, country["name"]["common"])
                showcountry(0)
            else:
                resultl.config(text=f"No countries found in {region}", fg="#3e4d34")
        else:
            resultl.config(text="Error getting region data", fg="#3e4d34")
                
    except urllib.error.HTTPError:
        resultl.config(text=f"Region '{region}' not found", fg="#3e4d34")
    except Exception as e:
        resultl.config(text=f"Error: {str(e)}", fg="#3e4d34")

def cleardisplay():
    """Clear all displayed content and reset the interface"""
    instructions.delete("1.0", END)
    countrylist.delete("1.0", END)
    flag_label.config(image='') # Clear flag image
    flag_label.config(text="") # Clear flag text
    resultl.config(text="", fg="#000000")
    listbox.delete(0, END)
    entry.delete(0, END)
    region_entry.delete(0, END)
    region_entry.insert(0, "e.g., Europe, Asia, Africa") # Restore placeholder text

# Label for searching the country
Label(root, text="Country name?", font=("Helvetica", 20, "bold"), fg="#3e4d34", bg="#9dc183").pack(pady=20)

# Entry widget for user to type country name
entry_frame = Frame(root, bg="#9dc183")
entry_frame.pack(pady=5)
entry = Entry(entry_frame, width=30, font=("Helvetica", 16), bg="#c5d8b0", fg="#000000")
entry.pack(side=LEFT, padx=5)

# Search country button 
searchb = Button(entry_frame, text="Search Country", font=("Helvetica", 14, "bold"),  
                 fg="#3e4d34", bg="#c5d8b0", activebackground="#a8c193", 
                 activeforeground="#3e4d34", command=search)
searchb.pack(side=LEFT, padx=5)

# Region search label
Label(root, text="Or search by region:", font=("Helvetica", 16, "bold"), 
      fg="#3e4d34", bg="#9dc183").pack(pady=20)

# Entry widget for region name
region_frame = Frame(root, bg="#9dc183")
region_frame.pack(pady=5)
region_entry = Entry(region_frame, width=30, font=("Helvetica", 16), bg="#c5d8b0", fg="#000000")
region_entry.pack(side=LEFT, padx=5)
region_entry.insert(0, "e.g., Europe, Asia, Africa") # Default placeholder text

# Region search button
regionb = Button(region_frame, text="Search by Region", font=("Helvetica", 14), 
                 fg="#3e4d34", bg="#c5d8b0", activebackground="#a8c193", 
                 activeforeground="#3e4d34", command=searchbyregion)
regionb.pack(side=LEFT, padx=5)

# Clear button
clearbutton = Button(root, text="Clear Display", font=("Helvetica", 14, "bold"), 
                     fg="#3e4d34", bg="#c5d8b0", activebackground="#a8c193", 
                     activeforeground="#3e4d34", command=cleardisplay)
clearbutton.pack(pady=20)

# Listbox to display multiple countries returned by search
Label(root, text="Search Results:", font=("Helvetica", 14, "bold"), 
      fg="#3e4d34", bg="#9dc183").pack(pady=10)
listbox_frame = Frame(root, bg="#c5d8b0", relief=SUNKEN, borderwidth=2)
listbox_frame.pack(pady=5)
listbox = Listbox(listbox_frame, width=50, height=3, bg="#c5d8b0", fg="#000000", 
                  font=("Helvetica", 10), selectbackground="#3e4d34", 
                  selectforeground="#c5d8b0")
listbox.pack(padx=5, pady=5)
listbox.bind("<<ListboxSelect>>", select)  # Bind selection event to select() function

# Label to display flag image (initially shows placeholder text)
flag_label = Label(root, text="Flag will appear here", font=("Helvetica", 12), 
                   fg="#3e4d34", bg="#9dc183", wraplength=400)
flag_label.pack(pady=10)

# Label to display country name
resultl = Label(root, text="", font=("Helvetica", 20, "bold"), 
                fg="#000000", bg="#9dc183")
resultl.pack(pady=10)

# Country info label
Label(root, text="Country Info:", font=("Helvetica", 16, "bold"), 
      fg="#3e4d34", bg="#9dc183").pack()

# Text widget to display country info
instructions_frame = Frame(root, bg="#c5d8b0")
instructions_frame.pack(pady=5)
instructions = Text(instructions_frame, wrap=WORD, width=55, height=10, 
                    bg="#c5d8b0", fg="#000000", font=("Helvetica", 10))
instructions.pack()

# Country details label 
Label(root, text="Country Details:", font=("Helvetica", 16, "bold"), 
      fg="#3e4d34", bg="#9dc183").pack()

# Text widget to display country details 
country_frame = Frame(root, bg="#c5d8b0")
country_frame.pack(pady=5)
countrylist = Text(country_frame, wrap=WORD, width=55, height=5, 
                   bg="#c5d8b0", fg="#000000", font=("Helvetica", 10))
countrylist.pack()

# Status bar at bottom of window
statusbar = Label(root, text="REST Countries API | Country Explorer with Flags", 
                  bd=1, relief=SUNKEN, anchor=W, font=("Helvetica", 8), 
                  fg="#3e4d34", bg="#c5d8b0")
statusbar.pack(side=BOTTOM, fill=X)

root.mainloop()  # Start the Tkinter event loop to keep GUI running