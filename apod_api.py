import requests
from datetime import date
'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
API_GET_URL = 'https://api.nasa.gov/planetary/apod'
API_KEY = '9hO2fAibprXw62bMNKtPxmi4pFG3iVqMbBlBuGWw'

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    query_params = {
    'api_key': API_KEY,
    'date': apod_date,
    'thumbs': True
    }
    header_params = {
    'Accept': 'application/json'
    }
    resp_msg = requests.get(API_GET_URL, params=query_params, headers=header_params)

    if resp_msg.status_code == requests.codes.ok:
    # Extract text file content from response message body
        apod_information = resp_msg.json()
        print(f"Getting {apod_date} APOD information from NASA...success")
        return apod_information

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    if apod_info_dict['media_type'] == 'image':
        image_url = apod_info_dict['hdurl']

    elif apod_info_dict['media_type'] == 'video':
        image_url = apod_info_dict['thumbnail_url']
    
    return image_url
