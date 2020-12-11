import re
import os
import json

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

JSON_URL = 'https://www.instagram.com/graphql/query/'

JS_PATTERN = r'static/bundles/es6/Consumer.js/\w*.js'
QUERY_HASH_PATTERN = r'profilePosts\.byUserId\.get[^,]+,queryId:"\w+"'
INTERNAL_DATA_PATTERN = r'window._sharedData\s=\s.+?;</script>'


def get_html(url, driver):
    """
    Gets html code in url
    """
    driver.get(url)
    html = driver.page_source
    return html

def get_data_from_html(container):
    """
    Takes all media from html's json. Additionaly returns
    profile id, next query's item cursor, and bool value of 
    the next query's existence 
    """
    data = {}
    media_urls = []
    
    try:
        user = container['entry_data']['ProfilePage'][0]['graphql']['user']
        profile_id = user['id']
        
        page = user['edge_owner_to_timeline_media']
        end_cursor = page['page_info']['end_cursor']
        has_next_page = page['page_info']['has_next_page']
        edges = page['edges'] 

        for edge in edges:
            slideshow = edge['node'].get('edge_sidecar_to_children')

            if slideshow:
                slideshow_edges = slideshow.get('edges')
                for slideshow_edge in slideshow_edges:
                    if slideshow_edge['node']['is_video']:
                        url = slideshow_edge['node']['video_url']
                    else:
                        url = slideshow_edge['node']['display_url']
                    media_urls.append(url)
            else:
                if edge['node']['is_video']:
                    url = edge['node']['video_url']
                else:
                    url = edge['node']['display_url']
                media_urls.append(url)

        data.update(
            {
                'profile_id': profile_id,
                'has_next_page': has_next_page, 
                'end_cursor': end_cursor,
                'media': media_urls
            }
        )
    except KeyError:
        # LOGGING TODO
        pass

    return data

def get_data_from_ajax(container):
    """
    Same as get_data_from_html(), but works with ajax's json
    """
    data = {}
    media_urls = []
    
    try:
        page = container['data']['user']['edge_owner_to_timeline_media']
        end_cursor = page['page_info']['end_cursor']
        has_next_page = page['page_info']['has_next_page']
        edges = page['edges'] 

        for edge in edges:
            slideshow = edge['node'].get('edge_sidecar_to_children')

            if slideshow:
                slideshow_edges = slideshow.get('edges')
                for slideshow_edge in slideshow_edges:
                    if slideshow_edge['node']['is_video']:
                        url = slideshow_edge['node']['video_url']
                    else:
                        url = slideshow_edge['node']['display_url']
                    media_urls.append(url)
            else:
                if edge['node']['is_video']:
                    url = edge['node']['video_url']
                else:
                    url = edge['node']['display_url']
                media_urls.append(url)

        data.update(
            {
                'has_next_page': has_next_page, 
                'end_cursor': end_cursor,
                'media': media_urls
            }
        )
    except KeyError:
        # LOGGING TODO
        pass

    return data

def get_query_hash(html):
    """
    Gets query_hash from the script, which downloads on background
    """
    query_hash = ''
    try:
        match = re.search(JS_PATTERN, html).group()
        script = requests.get('https://www.instagram.com/' + match).text
        
        match = re.search(QUERY_HASH_PATTERN, script).group()
        query_hash = match.split('"')[-2]
    except AttributeError:
        # LOGGING TODO
        pass

    return query_hash

def main():
    """
    Main function
    """
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    with open('profiles.txt') as file:
        for url in file:
            media = []
            html = get_html(url, driver)
            username = url.rstrip('/\n').split('/')[-1]

            print(f'Scrapping media from {username}')

            # Get data from HTML
            match = re.search(INTERNAL_DATA_PATTERN, html).group()
            match = match.lstrip('window._sharedData= ').rstrip(';</script>')
            container = json.loads(match)
            data = get_data_from_html(container)
            
            media.extend(data['media'])

            # Get data from AJAX
            profile_id = data['profile_id']
            query_hash = get_query_hash(html)
            while data['has_next_page']:
                variables = {
                    'id': profile_id,
                    'first': 12,
                    'after': data['end_cursor']
                }
                params = {
                    'query_hash': query_hash,
                    'variables': json.dumps(variables)
                }
                response = requests.get(JSON_URL, params=params)
                container = response.json()
                data = get_data_from_ajax(container)
                media.extend(data['media'])

            with open(f'profiles/{username}.txt', 'w') as f:
                for url in media:
                    f.write(url+'\n')

    print('Done.')
    driver.quit()


if __name__ == '__main__':
    main()
