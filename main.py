import re
import json
import csv
from time import sleep
from bs4 import BeautifulSoup
import requests

def extract_salary_info(job_title, job_city):
    # TAKES INFORMATION FROM salary.com
    template1 = 'https://www.salary.com/research/salary/alternate/{}-salary/{}'
    template2 = 'https://www.salary.com/research/salary/alternate/{}-salary/'
    template3 = 'https://www.salary.com/research/salary/listing/{}-salary/{}'
    template4 = 'https://www.salary.com/research/salary/listing/{}-salary/'
    template5 = 'https://www.salary.com/research/salary/benchmark/{}-salary/{}'
    template6 = 'https://www.salary.com/research/salary/benchmark/{}-salary/'
    template7 = 'https://www.salary.com/research/salary/position/{}-salary/{}'
    template8 = 'https://www.salary.com/research/salary/position/{}-salary/'
    template9 = 'https://www.salary.com/research/salary/hiring/{}-salary/{}'
    template10 = 'https://www.salary.com/research/salary/hiring/{}-salary/'
    
    job_title = job_title.replace(" ","-")
    job_city = job_city.replace(" ","-")

    script_found = False

    # links with 'alternate'
    url1 = template1.format(job_title, job_city)
    url2 = template2.format(job_title)

    # links with 'listing'
    url3 = template3.format(job_title, job_city)
    url4 = template4.format(job_title)

    # links with 'benchmark'
    url5 = template5.format(job_title, job_city)
    url6 = template6.format(job_title)

    # links with 'position'
    url7 = template7.format(job_title, job_city)
    url8 = template8.format(job_title)

    # links with 'hiring'
    url9 = template9.format(job_title, job_city)
    url10 = template10.format(job_title)

    urls = [url1,url2,url3,url4,url5,url6,url7,url8,url9,url10]
    for url in urls:
        if script_found:
            break

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                script = soup.find_all("script", {"type": "application/ld+json"})
                if script:
                    script_found = True
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch from URL: {e}")

    if not script_found:
        print("Webpage data not accesible!")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    script = soup.find_all("script", {"type": "application/ld+json"})
    script = script[1].string

    json_data = json.loads(script)

    job_title = json_data['name']
    location = json_data['occupationLocation'][0]['name']
    description = json_data['description']

    salary_info = json_data.get('estimatedSalary', [{}])[0]
    ntile_10 = salary_info.get('percentile10', 'Not Available')
    ntile_25 = salary_info.get('percentile25', 'Not Available')
    ntile_50 = salary_info.get('median', 'Not Available')
    ntile_75 = salary_info.get('percentile75', 'Not Available')
    ntile_90 = salary_info.get('percentile90', 'Not Available')

    salary_data = (job_title, location, description, ntile_10, ntile_25, ntile_50, ntile_75, ntile_90)
    return salary_data

def find_job_titles(search_query, page):
    template = "https://www.career.com/jobs/-by-title/{}?qk={}"

    url = template.format(page, search_query)
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except requests.exceptions.ConnectionError:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    job_elements = soup.find_all('h3', class_='crr-title')
    job_titles = [job.text.strip() for job in job_elements]

    return job_titles

def display_job_titles(job_titles, start_index=0, limit=10):
    end_index = start_index + limit
    job_subset = job_titles[start_index:end_index]
    
    print("Here are some job titles I found:")
    for idx, title in enumerate(job_subset, start=start_index+1):
        print(f"{idx}. {title}")
    
    return end_index

def ask_to_show_more(job_titles, start_index, limit=10):
    if start_index + limit < len(job_titles):
        user_input = input("\nWould you like to see more jobs on this page? (y/n): ").strip().lower()
        if user_input == 'y':
            return True
    return False

def main():
    
    search_query = input("Type a search query for a job title: ")
    job_titles = find_job_titles(search_query,1)

    start_index = 0
    limit = 10
    while start_index < len(job_titles):

        start_index = display_job_titles(job_titles, start_index, limit)

        if not ask_to_show_more(job_titles, start_index, limit):
            print("You can select a job or search for another job.")
            select_job = input("Would you like to select one of these jobs or not? (y/n): ")
            if select_job == "y":
                job_index = int(input("Select a number from 1 - 10 to select a position: "))
                job_query = str(job_titles[job_index-1]).lower()
                job_query = job_query.replace(" ","-")

                job_city = str(input("Type your target city (e.g. Dallas)): "))
                job_state = str(input("Type your target state (e.g. TX): "))
                job_location = (job_city+"-"+job_state).lower()

                job_data = extract_salary_info(job_query, job_location)
                print(job_data)
                break
            else:
                main()
            break

print("Welcome to the Job Salary CLI Tool!")
main()
