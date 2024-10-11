from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
import time
import difflib
import os

def move_and_clear_folder(src_dir, dest_dir):
    if os.path.exists(dest_dir):
        for file_name in os.listdir(dest_dir):
            file_path = os.path.join(dest_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
    else:
        os.makedirs(dest_dir)

    for file_name in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file_name)
        dest_file = os.path.join(dest_dir, file_name)
        os.rename(src_file, dest_file)

    for file_name in os.listdir(src_dir):
        file_path = os.path.join(src_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)

def extract_course_id(url):
        # Extract the course_id from the URL
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        course_id = query_params.get('id', [None])[0]
        if course_id is None:
            raise ValueError("URL does not contain a course_id")
        return course_id

def uncollapse_course_site(collapsesections_element):
    aria_expanded = collapsesections_element.get_attribute("aria-expanded")

    if aria_expanded == "false":
        for _ in range(3):
            collapsesections_element.click()
            time.sleep(0.5)  # Adding a small delay to ensure the clicks are registered
    elif aria_expanded == "true":
        for _ in range(2):
            collapsesections_element.click()
            time.sleep(0.5)  # Adding a small delay to ensure the clicks are registered
    
def fetch_site(driver, url, dir, delay=1):

    course_id = extract_course_id(url)
    
    driver.get(url)

    time.sleep(delay)  # Wait for the page to fully load

    collapsesections_element = driver.find_element(By.ID, "collapsesections")
    
    uncollapse_course_site(collapsesections_element)

    # Get the body part of the page
    body_element = driver.find_element(By.TAG_NAME, "body")
    
    # Extract text from specific tags
    tags = ['a', 'p', 'span', 'label']
    text_content = []
    for tag in tags:
        elements = body_element.find_elements(By.TAG_NAME, tag)
        for element in elements:
            text_content.append(element.text)

    # Join all text content into a single string
    text_content_str = "\n".join(text_content)

    # Create the directory if it does not exist
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Save the text content to a file
    course = f'{dir}/course_{course_id}.txt'

    # print(f"Saving course {course_id} to {course}")
    with open(course, 'w', encoding='utf-8') as file:
        file.write(text_content_str)

def compare_files_in_folders(dir1, dir2) -> bool:
    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))

    difference_detected = False

    common_files = files1.intersection(files2)

    for file_name in common_files:
        file1_path = os.path.join(dir1, file_name)
        file2_path = os.path.join(dir2, file_name)

        with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
            file1_content = file1.read()
            file2_content = file2.read()

            if file1_content != file2_content:
                difference_detected = True
                print(f"Difference found in: {file_name}")
                diff = difflib.unified_diff(
                    file1_content.splitlines(),
                    file2_content.splitlines(),
                    fromfile=f'{dir1}/{file_name}',
                    tofile=f'{dir2}/{file_name}',
                    lineterm=''
                )
                for line in diff:
                    print(line)
    
    if not difference_detected:
        print("No differences found!")
    
    return difference_detected


edge_driver = webdriver.Edge()

edge_driver.get("https://c2.etf.unsa.ba/login/index.php")

# If auth.txt does not exist, end program
if not os.path.exists('auth.txt'):
    print("auth.txt file does not exist. Please create the file with your credentials.")
    edge_driver.quit()
    exit()


# If c2_sites.txt does not exist, end program
if not os.path.exists('c2_sites.txt'):
    print("c2_sites.txt file does not exist. Please create the file with C2 course list.")
    edge_driver.quit()
    exit()

with open('auth.txt', 'r') as file:
    my_username = file.readline().strip()
    my_password = file.readline().strip()

username_field = edge_driver.find_element(By.ID, "username")
username_field.send_keys(my_username)
password_field = edge_driver.find_element(By.ID, "password")
password_field.send_keys(my_password)
login_button = edge_driver.find_element(By.ID, "loginbtn")
login_button.click()

baseline_dir = "Baseline"
tmp_dir = "Tmp"

# Check if the Baseline directory is empty
if not os.listdir(baseline_dir):
    with open('c2_sites.txt', 'r') as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        if url:
            fetch_site(edge_driver, url, baseline_dir)
else:
    # Create the Tmp directory if it does not exist
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    with open('c2_sites.txt', 'r') as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        if url:
            fetch_site(edge_driver, url, tmp_dir)
    
    print("\n\n")

    compare_files_in_folders("Baseline", "Tmp")

    move_and_clear_folder("Tmp", "Baseline")    
    

edge_driver.quit()
