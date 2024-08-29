import os
import subprocess


def get_last_page() -> str:
    last_page = ''
    max_pages = subprocess.getoutput("bash -c './max_pages.sh'")
    if max_pages.isdigit():
        last_page = max_pages
        print('Last page:', last_page)
    return last_page


def get_links() -> list:
    pages = get_last_page()
    links = []
    if pages:    
        list_links = subprocess.getoutput(f"bash -c './list_links.sh {pages}'")
        if list_links:
            links = list(filter(None, list_links.strip().split('\n')))
            print('Random number page:', links.pop(0))
            print(f'List:\n{links}')
    return links


def output_links() -> None:
    links = get_links()
    filename = 'creators.deepfake.txt'
    text = ''
	
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as txt:
            txt.write(text)
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
		
    if links:
        for item in links:   
            img_link = subprocess.getoutput(f"bash -c './img_link.sh {item}'")      
            if img_link.startswith('https'):
                for number, char in enumerate(img_link):
                    if char == '"':
                        img_link = img_link[:number]
                if img_link not in text:
                    with open(filename, 'a', encoding='utf-8') as txt:
                        txt.write(img_link + '\n')
                print('url:', img_link)
        return
    print('Not found')


output_links()
