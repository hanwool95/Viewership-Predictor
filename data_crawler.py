from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import csv


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
            viewer_ship_rate = self.search_viewer_ship_rate(target_word)
            if viewer_ship_rate:
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
    viewer_ship_searcher = Viewer_Ship(['신의 저울', '골 때리는 그녀들'], 'SBS')
    viewer_ship_searcher.find_viewer_ship_from_search_link()
    viewer_ship_searcher.save_by_csv()
