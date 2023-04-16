#ライブラリをインポート
import os
import requests 
import time 
from bs4 import BeautifulSoup

#一覧ページと詳細ページの件数
def inspection_num():
    url = 'https://sauna-ikitai.com/search?conditions%5B%5D=guest_type%23one_day_visit&conditions%5B%5D=sauna_type%23dry&conditions%5B%5D=target_gender%23is_male_available&ordering=ikitai_counts_desc&prefecture%5B%5D=tokyo&page=1'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    list_page_url = soup.find_all('li', class_='c-pagenation_link')
    list_page_num = int(list_page_url[len(list_page_url)-1].getText()) if list_page_url != [] else 1
    detail_page_num = int(str(soup.find('p', class_='p-result_number').getText()).replace(' ','').replace('件','').replace('検索結果',''))
    dic = {'list_page_num':list_page_num, 'detail_page_num':detail_page_num}
    return dic

#一覧ページのクローリングしそのページのhtmlを返す
#page_count: ページ数 list_page_num: 一覧ページの全ページ数
def crawling_list_page(page_count, list_page_num):
    url = 'https://sauna-ikitai.com/search?conditions%5B%5D=guest_type%23one_day_visit&conditions%5B%5D=sauna_type%23dry&conditions%5B%5D=target_gender%23is_male_available&ordering=ikitai_counts_desc&prefecture%5B%5D=tokyo&page={}'.format(page_count)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    #html_filesが存在しない場合には作成する
    if not os.path.exists('./html_files'):
        os.mkdir('./html_files')
    #./html_files/sauna_list_pageが存在しない場合には作成する
    if not os.path.exists('./html_files/sauna_list_page'):
        os.mkdir('./html_files/sauna_list_page')
    with open('./html_files/sauna_list_page/page{}.html'.format(page_count),'w',encoding='UTF-8',errors='replace') as file:
        file.write(response.text)
    #進捗確認
    if page_count % 10 == 0:
        print('一覧ページ：{}/{} クローリング完了'.format(page_count, list_page_num))
    if page_count % 10 != 0 & page_count == list_page_num:
        print('一覧ページ：{}/{} クローリング完了'.format(page_count, list_page_num)) 
    time.sleep(1)
    return soup

#詳細ページのurlリストを返す関数
#soup: 該当の一覧ページのhtml lst: 詳細ページのurlリスト
def urls_list_page(soup,lst=[]):
    results = soup.find_all('div',class_='p-saunaItem')
    for result in results:
        lst.append(result.find('a').get('href'))
    return lst

#詳細ページをクローリングする
#url: 詳細ページへURL page_count: ページ数, detail_page_num: 詳細ページの全ページ数
def crawlimg_detail_page(url, page_count, detail_page_num):
    #file_pathが存在しない場合には作成する
    if not os.path.exists('./html_files/sauna_detail_page'):
        os.mkdir('./html_files/sauna_detail_page')
    response = requests.get(url)
    with open('./html_files/sauna_detail_page/page{}.html'.format(page_count),'w',encoding='UTF-8', errors='replace') as file:
        file.write(response.text)
    #進捗確認
    if page_count % 10 == 0:
        print('詳細ページ：{}/{} クローリング完了'.format(page_count, detail_page_num))
    if page_count % 10 != 0 & page_count == detail_page_num:
        print('詳細ページ：{}/{} クローリング完了'.format(page_count, detail_page_num))
    time.sleep(1)

#メイン関数
def main():
    list_page_num = inspection_num().get('list_page_num') #一覧ページのページ数
    detail_page_num = inspection_num().get('detail_page_num') #詳細ページ検索件数
    lst=[] #詳細ページのurlを格納する配列
    for i in range(1,list_page_num+1):
        soup = crawling_list_page(page_count=i, list_page_num=list_page_num)
        lst = urls_list_page(soup=soup, lst=lst)
    for i in range(1,len(lst)+1):
        crawlimg_detail_page(lst[i-1],page_count=i,detail_page_num=detail_page_num)
    #検収条件を確認
    print('#####################################################################')
    print('検収条件：{}件'.format(detail_page_num))
    sauna_detail_page_file_num = len(os.listdir('./html_files/sauna_detail_page')) #保存した詳細ページのファイル数
    if detail_page_num == sauna_detail_page_file_num:
        print('検収条件を満たしています。')
    else:
        print('検収条件を満たしていません。')
    print('#####################################################################')

   
if __name__ == '__main__':
    main()
    
