from bs4 import BeautifulSoup
from datetime import datetime
import requests
import csv
import logging
import os

logging.basicConfig(filename='requests.log', level=logging.INFO)
logger = logging.getLogger(__name__)


class HindustanTimes(object):
    """Main class to scrap the news web page."""

    def __init__(self, num_pages):
        """
        Init HindustanTimes.
        :param num_pages: The number of pages to scrap
        """
        # website url
        self.url_str = "https://www.hindustantimes.com/latest-news/"

        # path to save the scraped data in csv
        current_path = os.getcwd()
        self.file_path = "{}/fetched_data/HindustanTimes".format(current_path)

        self.num_pages = num_pages
        try:
            if not os.path.exists(self.file_path):
                os.makedirs(self.file_path)
        except Exception:
            logger.error({'message': "Unable to create directory!"})

    def get_article_urls(self):
        """
        Get a list of article links.
        :return: list(tuple): [(article date, article link)]
        """
        # get latest date
        search_date_obj = datetime.today()
        page_no = 1
        all_article_links = []

        # fetch first num_pages number of  pages
        while page_no <= self.num_pages:
            url_str = "{}?pageno={}".format(self.url_str, page_no)

            # hit the web page and create a soup object
            search_result = requests.get(url_str)
            soup = BeautifulSoup(search_result.text, "html.parser")

            # find the latest articles and store their urls
            all_article_ul = soup.find("ul", class_="latest-news-bx more-latest-news more-separate")
            all_article_divs = all_article_ul.findAll("div", class_="media-body")
            for each_article_div in all_article_divs:
                # publish_date: Jul 18, 2020 15:53
                publish_date = each_article_div.find("span").text

                # convert publish date to a datetime object
                publish_date = publish_date.replace(',', '')
                publish_date_obj = datetime.strptime(publish_date, '%b %d %Y %H:%M')

                # skip the articles that are not today's.
                if not publish_date_obj.date() == search_date_obj.date():
                    continue

                # store urls of the latest(today's) articles
                article_link = each_article_div.find("a", href=True)["href"]
                all_article_links.append((publish_date_obj, article_link))

            print("Scraped page no. " + str(page_no))

            # increment page number
            page_no += 1

        logger.info({'message': "fetched url of all articles", 'url': self.url_str})
        return all_article_links

    def extract(self):
        """
        Scrap the given number of pages and store in a  csv.
        """
        try:
            all_list = []
            # get list of article urls
            all_article_links = self.get_article_urls()

            # scrap each article individually using the urls stored earlier
            for count, article_data in enumerate(all_article_links):
                article = requests.get(article_data[1])
                article_soup = BeautifulSoup(article.text, "html.parser")
                title = article_soup.title.text

                # get meta attributes
                head = article_soup.find("head")
                published_date = article_data[0].strftime("%d/%m/%Y")
                article_url = head.find("meta", property="og:url")["content"]
                summary = head.find("meta", property="og:description")["content"]

                # get first paragraph of the content
                content_div = article_soup.find("div", class_="storyDetail")
                para = ""
                if content_div:
                    paragraphs = content_div.find_all("p")
                    for paragraph in paragraphs:
                        if paragraph and paragraph.text != "":
                            para += paragraph.text

                data = {'publish_date': published_date, 'headline': title, 'href': article_url, 'summary': summary,
                        'channel': 'HindustanTimes', 'source': '', 'content': para}
                all_list.append(data)
                print("Scraped article no. " + str(count + 1))

            logger.info({'message': "Scraped data of all articles", 'number of articles': len(all_article_links)})
            self.save_data(all_list)
        except Exception:
            logger.error({'message': "Unable to fetch data"})

    def save_data(self, data):
        """
        Save the given scraped data into a csv.
        :param data: list(dict), list of articles data
        """
        try:
            to_csv = data
            keys = to_csv[0].keys()
            with open(self.file_path + '/data.csv', 'w', encoding='utf8', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(to_csv)
                logger.info({'message': "Saved all articles in csv"})
        except Exception:
            logger.error({'message': "Error while dumping data in csv!"})
