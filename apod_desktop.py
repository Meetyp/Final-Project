""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import os
import image_lib
import inspect
import sys
import sqlite3
import apod_api
import image_lib
import re
import hashlib

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    num_params = len(sys.argv) - 1
    if num_params >= 1:
        try:
            apod_date = date.fromisoformat(sys.argv[1])
        except ValueError as err:
            print(f"Error: Invalid date format; {err}")
            sys.exit("Script execution aborted")

        MIN_APOD_DATE = date.fromisoformat("1995-06-16")
        if apod_date < MIN_APOD_DATE:
            print(f"Error: Date too far in past; First APOD was on {MIN_APOD_DATE.isoformat()}")
            sys.exit("Script execution aborted")
        elif apod_date > date.today():
            print("Error: APOD date cannot be in the future")
            sys.exit("Script execution aborted")
    else:
        apod_date = date.today()

    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    
    global image_cache_dir
    global image_cache_db

    # Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir, 'APOD')

    # Create the image cache directory if it does not already exist
    print(f"Image cache directory: {image_cache_dir}")
    isExist = os.path.exists(image_cache_dir)
    if not isExist:
        os.mkdir(image_cache_dir)
        print("Image cache directory created.")
    else:
        print("Image cache directory already exists.")

    # Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

    # Create the DB if it does not already exist
    isPresent = os.path.exists(image_cache_db)
    print(f"Image cache DB: {image_cache_db}")
    if not isPresent:
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        create_album_table_query = """
            CREATE TABLE IF NOT EXISTS images_info
            (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                explanation TEXT NOT NULL,
                path TEXT NOT NULL,
                sha256 TEXT NOT NULL
            );
        """
        cur.execute(create_album_table_query)
        con.commit()
        con.close()
        print("Image cache DB created.")
    else:
        print("Image cache DB already exists.")

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())
    # Download the APOD information from the NASA API
    apod_information = apod_api.get_apod_info(apod_date)
    apod_title = apod_information['title']
    print(f"APOD title: {apod_title}")
    apod_explanation = apod_information['explanation']
    

    # Download the APOD image
    image_file_url = apod_api.get_apod_image_url(apod_information)
    print(f"APOD URL: {image_file_url}")

    final_image = image_lib.download_image(image_file_url)
    print(f"Downloading image from {image_file_url}...success")

    image_sha256 = hashlib.sha256(final_image).hexdigest()
    print(f"APOD SHA-256: {image_sha256}")

    apod_filepath = determine_apod_file_path(apod_title, image_file_url)

    # Check whether the APOD already exists in the image cache
    image_id = get_apod_id_from_db(image_sha256)

    # Save the APOD file to the image cache directory
    try:
        if image_id == 0:
            print("APOD image is not already in cache.")
            print(f"APOD file path: {apod_filepath}")
            image_lib.save_image_file(final_image, apod_filepath)
            
        # Add the APOD information to the DB
            record_id = add_apod_to_db(apod_title, apod_explanation, apod_filepath, image_sha256)
            return record_id
        print("APOD image is already in cache.")
        return image_id
    except Exception as err:
        print(f"Error: {err}")
        return 0

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    
    try:
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        query = """
                INSERT INTO images_info
                (
                    title,
                    explanation,
                    path,
                    sha256
                )
                VALUES (?, ?, ?, ?);
            """
        query_data = (title, explanation, file_path, sha256)
        cur.execute(query, query_data)
        con.commit()
        con.close()
        print("Adding APOD to image cache DB...success")
        return cur.lastrowid
    except:
        return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    query = """
            SELECT id FROM images_info
            WHERE sha256 = ?;
            """
    query_data = (image_sha256, )
    cur.execute(query, query_data)
    query_result = cur.fetchone()
    con.close()
    if query_result is not None:
        return query_result[0]
    return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    file_extension = os.path.splitext(image_url)[1]
    creating_file_name = image_title.strip().replace(" ", "_")
    file_name = re.sub('[\W]+', '', creating_file_name) + file_extension
    
    file_path = os.path.join(get_script_dir(), 'APOD', file_name)
    return file_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # Query DB for image info
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    query = """
            SELECT title, explanation, path FROM images_info
            WHERE id = ?;
            """
    query_data = (str(image_id), )
    cur.execute(query, query_data)
    query_result = cur.fetchone()
    con.close()

    # Put information into a dictionary
    apod_info = {
        'title': query_result[0], 
        'explanation': query_result[1],
        'file_path': query_result[2],
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    query = """
            SELECT title FROM images_info;
            """
    cur.execute(query)
    query_result = cur.fetchall()
    con.close()
    # NOTE: This function is only needed to support the APOD viewer GUI
    title_list = [i[0] for i in query_result]
    return title_list

if __name__ == '__main__':
    main()