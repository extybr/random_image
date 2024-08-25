import subprocess
import os

pages = 0
links = []
img_link = ''

max_pages = subprocess.getoutput("bash -c './max_pages.sh'")
if max_pages.isdigit():
    pages = max_pages
    print('Last page:', pages)

if pages:    
    list_links = subprocess.getoutput(f"bash -c './list_links.sh {pages}'")
    if list_links:
        links = list_links.strip().split('\n')
        [links.remove(i) for i in links if not i]
        print('List:\n', links)

filename = 'creators.deepfake.txt'
text = ''
if not os.path.exists(filename):
    with open(filename, 'w', encoding='utf-8') as txt:
        txt.write(text)
else:
     with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
if links:
    for item in links:   
        img_link = subprocess.getoutput(f"bash -c './img_link.sh {item}'")      
        if img_link.startswith('https'):
            for i, chr in enumerate(img_link):
                if chr == '"':
                    img_link = img_link[:i]
            if img_link not in text:
                with open(filename, 'a', encoding='utf-8') as txt:
                    txt.write(img_link + '\n')
            print('url:', img_link)
 
