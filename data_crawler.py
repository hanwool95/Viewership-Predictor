from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class SBS_Program_information:
    def __init__(self, target_url):
        self.target_url = target_url
        self.programs_div_class = "tv_list_w"
        self.program_li_class = "tv_list_cont"

        self.urls = []

        self.all_program_informations = []

    def search_app_programs(self):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome('./chromedriver', options=options)
        driver.get(url=self.target_url)

        y_state = 1500
        for i in range(40):
            target_str = "window.scrollTo(0, " + str(y_state) +")"
            driver.execute_script(target_str)
            time.sleep(1)
            y_state += 1500
        content_elements = driver.find_elements(By.CLASS_NAME, "tv_list_cont")
        for content_element in content_elements:
            a_tag = content_element.find_element(By.TAG_NAME, "a")
            url = a_tag.get_attribute('href')
            self.urls.append(url)

    def find_program_information_by_urls(self):

        for i, target_url in enumerate(self.urls):
            if i > 42:
                try:
                    information_url = ""

                    options = webdriver.ChromeOptions()
                    driver = webdriver.Chrome('./chromedriver', options=options)
                    driver.get(url=target_url)
                    time.sleep(2)
                    inside_urls = driver.find_elements(By.TAG_NAME, "a")

                    for inside_url in inside_urls:
                        target_inside_url = inside_url.get_attribute('href')
                        if '/about/' in target_inside_url:
                            information_url = target_inside_url

                    if information_url:
                        information_dict = self.get_information_from_information_url(information_url, driver)
                        self.all_program_informations.append(information_dict)
                    else:
                        print("not found")
                        print(target_url)
                except:
                    print("program error")
                    print(target_url)

    def get_information_from_information_url(self, information_url: str, driver) -> dict:
        driver.get(url=information_url)
        time.sleep(2)
        title_element = driver.find_element(By.CLASS_NAME, 'pi_title')
        name = title_element.text

        date = ""
        form = ""
        pd = ""
        writer = ""
        cast = ""

        plan_element = driver.find_element(By.CLASS_NAME, 'tmct_text')
        plan = plan_element.text

        lis = driver.find_elements(By.CLASS_NAME, 'pidl_inner')

        for li in lis:
            title = li.find_element(By.TAG_NAME, 'strong').text
            value = li.find_element(By.TAG_NAME, 'span').text

            if title == "방송기간":
                date = value
            elif title == "편성":
                form = value
            elif title == "연출":
                pd = value
            elif title == "극본":
                writer = value
            elif title == "출연":
                cast = value
        result_dict = {'이름': name, '기간':date, '편성': form, '연출': pd, '극본': writer, '출연': cast, '기획의도': plan,
                       'url': information_url}


        return result_dict

    def save_all_program_information_by_csv(self):
        with open('sbs_program_inform.csv', 'w', encoding='utf-8-sig') as file:
            write = csv.writer(file)
            for program_information in self.all_program_informations:
                write.writerow([program_information['이름'], program_information['기간'], program_information['편성'],
                                program_information['연출'], program_information['극본'], program_information['출연'],
                                program_information['기획의도'], program_information['url']])



class Viewer_Ship:
    def __init__(self, search_names: list, broad_cast: str):
        self.search_link = "https://search.naver.com/search.naver?query="
        self.highest_viewer_ship_div_class = "rating_bx tag_highest"
        self.chart_class = "chart_box _chart"
        self.target_value = 'data-value'

        self.broad_cast = broad_cast

        self.search_names = search_names

        self.__viewer_ship_rates = {}

    def find_viewer_ship_from_search_link(self):
        for search_name in self.search_names:
            target_word = self.broad_cast + " " + search_name + " " + "시청률"
            target_word = quote(target_word)
            time.sleep(1)
            viewer_ship_rate = self.search_viewer_ship_rate(target_word)
            self.__viewer_ship_rates[search_name] = viewer_ship_rate

    def search_viewer_ship_rate(self, target_name: str):
        target_url = self.search_link + target_name
        try:
            with urllib.request.urlopen(target_url) as url:
                doc = url.read()
                soup = BeautifulSoup(doc, "html.parser")
                highest_content = soup.find('div', self.highest_viewer_ship_div_class)
                chart_content = highest_content.find('div', self.chart_class)
                viewer_ship_rate = chart_content['data-value']

                return viewer_ship_rate
        except:
            return ""

    def get_viewer_ship_rates(self):
        return self.__viewer_ship_rates

    def save_by_csv(self):
        with open(self.broad_cast+'시청률목록.csv', 'w') as file:
            write = csv.writer(file)
            for name, rate in self.__viewer_ship_rates.items():
                write.writerow([name, rate])


if __name__ == "__main__":
    # program_crawler = SBS_Program_information('https://www.sbs.co.kr/ko/tv/drama')
    # program_crawler.search_app_programs()
    # program_crawler.find_program_information_by_urls()
    # program_crawler.save_all_program_information_by_csv()

    programs = []
    with open('total_information.csv', 'r', encoding='utf-8') as file:
        spamreader = csv.reader(file, delimiter=',')
        for row in spamreader:
            programs.append(row[1])
    print(programs)
    viewer_ship_searcher = Viewer_Ship(programs, 'SBS')
    viewer_ship_searcher.find_viewer_ship_from_search_link()
    viewer_ship_searcher.save_by_csv()