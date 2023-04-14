import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json


text_for_search_list = ['junior developer', 'middle developer', 'senior developer']
experience_param_list = ['noExperience', 'between1And3', 'between3And6', 'moreThan6']
columns_name = ['company name', 'city', 'vacancy name', 'salary from', 'salary to', 'salary currency',
                'work experience from', 'work experience to', 'employment', 'schedule', 'key skills', 'grade']
dollar_rate = 82.18
euro_rate = 90
user_headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
}


def save_hh_vacancies_on_csv():
    df_vacancies_data = pd.DataFrame(columns=columns_name)
    df_vacancies_data.to_csv('vacancies_data.csv', index=False)
    for text in text_for_search_list:
        for experience in experience_param_list:
            df_vacancies_data = pd.concat([df_vacancies_data, processing_vacancies_data(text, experience)])
            df_vacancies_data.to_csv('vacancies_data.csv', mode='a', index=False, header=False)
            df_vacancies_data.drop(df_vacancies_data.index, inplace=True)


def processing_vacancies_data(text_for_search, experience_param):
    df_vacancies_data = pd.DataFrame(columns=columns_name)
    for page in range(10):
        vacancies_info_on_page = json.loads(parse_vacancies_info(text_for_search, experience_param, page))
        print(vacancies_info_on_page['pages'])
        for one_vacancy_info in vacancies_info_on_page['items']:
            grade = text_for_search.split()[0]
            correct_form_of_data = data_to_correct_form_for_dataframe(one_vacancy_info, grade)
            df_vacancies_data.loc[len(df_vacancies_data.index)] = correct_form_of_data

        if vacancies_info_on_page['pages'] - page <= 1:
            break

    return df_vacancies_data


def parse_vacancies_info(text_for_search, experience_param, page=0):
    api_params = {
        'text': text_for_search,
        'area': '113',
        'page': page,
        'per_page': 100,
        'experience': experience_param
    }

    server_response = requests.get('https://api.hh.ru/vacancies', api_params, headers=user_headers)
    vacancies_info = server_response.content.decode()
    return vacancies_info


def data_to_correct_form_for_dataframe(one_vacancy_info, grade):
    company_name = one_vacancy_info['employer']['name']
    city = one_vacancy_info['area']['name']
    vacancy_name = one_vacancy_info['name']

    if one_vacancy_info['salary'] is None:
        salary_from, salary_to, salary_currency = None, None, None
    else:
        salary_from = one_vacancy_info['salary']['from']
        salary_to = one_vacancy_info['salary']['to']
        salary_currency = one_vacancy_info['salary']['currency']

    work_experience = one_vacancy_info['experience']['name']
    work_experience_from = None
    work_experience_to = None
    num_work_exp = re.findall(r'\d', work_experience)
    if len(num_work_exp) > 0:
        work_experience_from = num_work_exp[0]
    if len(num_work_exp) == 2:
        work_experience_to = num_work_exp[1]
    employment = one_vacancy_info['employment']['name']

    vacancy_url = one_vacancy_info['alternate_url']
    server_response = requests.get(vacancy_url, headers=user_headers)
    soup = BeautifulSoup(server_response.text, 'lxml')
    schedule = soup.find('p', attrs={'data-qa': 'vacancy-view-employment-mode'}).find('span').text
    # schedule = one_vacancy_info['schedule']['name']
    key_skills = soup.find_all(class_='bloko-tag__section bloko-tag__section_text')
    key_skills = [skill.text.replace('\xa0', ' ') for skill in key_skills]
    # key_skills = []
    # if one_vacancy_info['key_skills'] != 0:
    #     key_skills = [skill['name'] for skill in one_vacancy_info['key_skills']]
    key_skills = ', '.join(key_skills)

    correct_form = [company_name, city, vacancy_name, salary_from, salary_to, salary_currency,
                    work_experience_from, work_experience_to, employment, schedule, key_skills, grade]
    return correct_form


def data_to_correct_form_for_message(one_vacancy_info):
    correct_form = []
    vacancy_url = one_vacancy_info['alternate_url']
    return


save_hh_vacancies_on_csv()
