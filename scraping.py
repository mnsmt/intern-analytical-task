#ライブラリをインポート
import os
import csv 
from bs4 import BeautifulSoup


#htmlファイルを読み込む関数
#file_path: 読み込むファイルが保存されているディレクトリのパス page_count:該当htmlファイルのページ数
def read_html_file(file_path,page_count):
    with open('{}/page{}.html'.format(file_path,page_count), 'r', encoding='UTF-8') as f:
        html_file = f.read()
    soup = BeautifulSoup(html_file,'lxml')
    return soup

#csvファイルを作成する関数
#columns: csvファイルのカラム名(配列型)
def make_csv_file(columns):
    with open('sauna.csv', 'w', newline='', encoding='CP932', errors='replace') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

#csvファイルにデータを追加する
#dic: カラム名とそれに対応する値(辞書型) columns: カラム名
def write_csv_file(dic={}, columns=[]):
    with open('sauna.csv', 'w', newline='', encoding='CP932', errors='replace') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writerow(dic)

#一覧ページからサウナ名と入浴料をスクレイピングして関数辞書型で返す
#soup: htmlファイルのテキスト sauna_price_dic: サウナの名前と入浴料(辞書型)
def scraping_sauna_price(soup,sauna_price_dic):
    price_lst=[]
    sauna_names=soup.find_all('div',class_='p-saunaItemName')
    sauna_info=soup.find_all('li',class_='p-saunaItem_information')
    for i in range(len(sauna_info)):
        info=str(sauna_info[i].getText())
        if '入浴料' in info:
            price_lst.append(info.replace('入浴料：',''))
    for i in range(len(sauna_names)):
        sauna_name = str(sauna_names[i].find('h3').getText().replace('\n','').replace(' ',''))
        sauna_price = price_lst[i]
        sauna_price_dic_new = {sauna_name: sauna_price}
        sauna_price_dic = {**sauna_price_dic, **sauna_price_dic_new}
    return sauna_price_dic

#サウナ詳細ページのスクレイピングを行う。入浴料を追加して全カラムについての情報を関数辞書型で返す
##soup: 該当詳細ページのhtml  sauna_price_dic: サウナの名前と入浴料(辞書型)
def scraping_detail_page(soup,sauna_price_dic):
    name = soup.find('span', class_ = 'c-headline_string').getText().replace('\n','').replace(' ','')
    location = soup.find('p', class_ = 'p-saunaDetailHeader_area').getText().replace('\n','').replace(' ','')
    ikitai = soup.find('div',class_='p-action_number').getText().replace('\n','').replace(' ','')
    
    #男湯の情報のみを抽出
    soup_sauna_info=soup.find('div',attrs={'class':'c-tab_content js-tabContent','data-tab':'men'})
    
    #サウナ基本情報
    sauna_item = soup_sauna_info.find_all('div', class_ = 'p-saunaSpecItem--sauna')
    sauna_temp=[]
    sauna_capa=[]
    for i in range(len(sauna_item)):
        #サウナの温度
        soup_sauna_temp = str(sauna_item[i].find('p','p-saunaSpecItem_number')).replace('<p class="p-saunaSpecItem_number">','').replace('</p>','').replace('<span>','').replace('</span>','').replace('<strong>','').replace('</strong>','').replace('\n','').replace(' ','').replace('温度','').replace('度','')
        if soup_sauna_temp != 'None' and soup_sauna_temp!='-' and soup_sauna_temp!='?':
            sauna_temp.append(float(soup_sauna_temp))
        #サウナの収容人数
        soup_sauna_num = str(sauna_item[i].find('p','p-saunaSpecItem_people')).replace('<p class="p-saunaSpecItem_people">','').replace('</p>','').replace('\n','').replace(' ','').replace('収容人数：','').replace('人','')
        if soup_sauna_num != 'None' and soup_sauna_num != '-':
            sauna_capa.append(int(soup_sauna_num))
    sauna_temperature = str(max(sauna_temp)) if sauna_temp!=[] else None #最も高い温度をサウナの温度として採用
    sauna_capacity =  str(max(sauna_capa)) if sauna_capa!=[] else None#最も多い人数を収容人数として採用

    #水風呂基本情報
    cold_bath_item = soup_sauna_info.find_all('div', class_ = 'p-saunaSpecItem--mizuburo')
    cold_bath_temp = []
    cold_bath_capa = []
    for i in range(len(cold_bath_item)):
        #水風呂温度
        soup_cold_bath_temp = str(cold_bath_item[i].find('p','p-saunaSpecItem_number')).replace('<p class="p-saunaSpecItem_number">','').replace('</p>','').replace('<span>','').replace('</span>','').replace('<strong>','').replace('</strong>','').replace('\n','').replace(' ','').replace('温度','').replace('度','')
        if soup_cold_bath_temp != 'None' and soup_cold_bath_temp!='-' and soup_cold_bath_temp!='?':
            cold_bath_temp.append(float(soup_cold_bath_temp))
        #水風呂収容人数
        soup_cold_bath_num = str(cold_bath_item[i].find('p','p-saunaSpecItem_people')).replace('<p class="p-saunaSpecItem_people">','').replace('</p>','').replace('\n','').replace(' ','').replace('収容人数：','').replace('人','')
        if soup_cold_bath_num != 'None' and soup_cold_bath_num != '-':
            cold_bath_capa.append(int(soup_cold_bath_num))
    cold_bath_temperature = str(min(cold_bath_temp)) if cold_bath_temp!=[] else None #最も低い温度を水風呂の温度として採用
    cold_bath_capacity =  str(max(cold_bath_capa)) if cold_bath_capa!=[] else None#最も多い人数を収容人数として採用

    #サウナのスペック基本情報
    sauna_spec_table = soup_sauna_info.find('table', class_='p-saunaSpecTable')
    lst_sauna_spec=sauna_spec_table.find_all('img')
    if lst_sauna_spec == []:
        auf_laury = None
        auto_laury = None
        self_laury = None
        outside_refresh_space = None
        refresh_space = None
        ion_water = None
    else:
        if 'alt="有り"' in str(lst_sauna_spec[0]):
            auf_laury = '有り'
        elif 'alt="無し"' in str(lst_sauna_spec[0]):
            auf_laury = '無し'
        else:
            None

        if 'alt="有り"' in str(lst_sauna_spec[1]):
            auto_laury = '有り'
        elif 'alt="無し"' in str(lst_sauna_spec[1]):
            auto_laury = '無し'
        else:
            None

        if 'alt="有り"' in str(lst_sauna_spec[2]):
            self_laury = '有り'
        elif 'alt="無し"' in str(lst_sauna_spec[2]):
            self_laury = '無し'
        else:
            None
        
        if 'alt="有り"' in str(lst_sauna_spec[3]):
            outside_refresh_space = '有り'
        elif 'alt="無し"' in str(lst_sauna_spec[3]):
            outside_refresh_space = '無し'
        else:
            None

        if 'alt="有り"' in str(lst_sauna_spec[4]):
            refresh_space = '有り'
        elif 'alt="無し"' in str(lst_sauna_spec[4]):
            refresh_space = '無し'
        else:
            None

        if 'alt="有り"' in str(lst_sauna_spec[5]):
            ion_water = '有り'
        elif 'alt="無し"' in str(lst_sauna_spec[5]):
            ion_water = '無し'
        else:
            None

    #設備ルール、支払い方法、アメニティ、リラクゼーション
    #0:無し 1:有り
    sauna_detail_spec_table = soup.find_all('span',class_='p-saunaSpecList_value')
    open_all_hours = sauna_detail_spec_table[0].getText()
    rest_space = sauna_detail_spec_table[1].getText()
    eat_space = sauna_detail_spec_table[2].getText()
    comic_book = sauna_detail_spec_table[3].getText()
    wifi = sauna_detail_spec_table[4].getText()
    electrical_outlet = sauna_detail_spec_table[5].getText()
    working_space = sauna_detail_spec_table[6].getText()
    water_dispenser = sauna_detail_spec_table[7].getText()
    parking_lot = sauna_detail_spec_table[8].getText()
    washlet = sauna_detail_spec_table[9].getText()
    bedrock_bath = sauna_detail_spec_table[10].getText()
    tattoo = sauna_detail_spec_table[11].getText()
    cash = sauna_detail_spec_table[12].getText()
    credit_card = sauna_detail_spec_table[13].getText()
    electronic_money = sauna_detail_spec_table[14].getText()
    shampoo = sauna_detail_spec_table[15].getText()
    conditioner = sauna_detail_spec_table[16].getText()
    body_soap = sauna_detail_spec_table[17].getText()
    face_soap = sauna_detail_spec_table[18].getText()
    razor = sauna_detail_spec_table[19].getText()
    toothbrush = sauna_detail_spec_table[20].getText()
    nylon_towel = sauna_detail_spec_table[21].getText()
    hairdryer = sauna_detail_spec_table[22].getText()
    unlimited_use_of_sauna_pants = sauna_detail_spec_table[23].getText()
    lotion = sauna_detail_spec_table[24].getText()
    milky_lotion = sauna_detail_spec_table[25].getText()
    makeup_remover = sauna_detail_spec_table[26].getText()
    cotton_swab = sauna_detail_spec_table[27].getText()
    body_care = sauna_detail_spec_table[28].getText()
    akasuri = sauna_detail_spec_table[29].getText()
    traditional_thai = sauna_detail_spec_table[30].getText()
    head_spa = sauna_detail_spec_table[31].getText()

    #入浴料
    sauna_price=sauna_price_dic.get(str(name))

    dic = {
        'name':name, 'location':location, 'sauna_temperature':sauna_temperature,
        'sauna_capacity':sauna_capacity, 'cold_bath_temperature':cold_bath_temperature,'cold_bath_capacity':cold_bath_capacity,
        'auf_laury':auf_laury, 'auto_laury':auto_laury,'self_laury':self_laury,
        'outside_refresh_space':outside_refresh_space, 'refresh_space': refresh_space, 'ion_water':ion_water,
        'open_all_hours':open_all_hours, 'rest_space':rest_space, 'eat_space':eat_space, 'comic_book':comic_book,
        'wifi': wifi, 'electrical_outlet': electrical_outlet, 'working_space': working_space, 'water_dispenser': water_dispenser,
        'parking_lot': parking_lot, 'washlet': washlet, 'bedrock_bath': bedrock_bath, 'tattoo': tattoo, 'cash': cash,
        'credit_card': credit_card, 'electronic_money': electronic_money, 'shampoo': shampoo, 'conditioner': conditioner,
        'body_soap': body_soap, 'face_soap': face_soap, 'razor': razor, 'toothbrush': toothbrush, 'nylon_towel': nylon_towel,
        'hairdryer': hairdryer, 'unlimited_use_of_sauna_pants': unlimited_use_of_sauna_pants, 'lotion': lotion,
        'milky_lotion': milky_lotion, 'makeup_remover': makeup_remover, 'cotton_swab': cotton_swab, 'body_care': body_care,
        'akasuri': akasuri, 'traditional_thai': traditional_thai, 'head_spa': head_spa,
        'sauna_price': sauna_price, 'ikitai': ikitai
    }
    return dic

#メイン関数
def main():
    sauna_list_page_file_path = './html_files/sauna_list_page' #一覧ページへのパス
    sauna_list_page_file_num = len(os.listdir(path=sauna_list_page_file_path)) #一覧ページのページ数
    sauna_detail_page_file_path = './html_files/sauna_detail_page' #詳細ページのへのパス
    sauna_detail_page_file_num = len(os.listdir(path=sauna_detail_page_file_path)) #詳細ページのページ数
    #カラム名
    columns=[
        'name', 'location', 'sauna_temperature',
        'sauna_capacity', 'cold_bath_temperature', 'cold_bath_capacity',
        'auf_laury', 'auto_laury', 'self_laury',
        'outside_refresh_space', 'refresh_space', 'ion_water',
        'open_all_hours', 'rest_space', 'eat_space',
        'comic_book', 'wifi', 'electrical_outlet', 
        'working_space', 'water_dispenser', 'parking_lot', 
        'washlet', 'bedrock_bath', 'tattoo', 
        'cash','credit_card', 'electronic_money', 
        'shampoo', 'conditioner', 'body_soap', 
        'face_soap', 'razor', 'toothbrush', 
        'nylon_towel', 'hairdryer', 'unlimited_use_of_sauna_pants', 
        'lotion', 'milky_lotion', 'makeup_remover', 
        'cotton_swab', 'body_care', 'akasuri', 
        'traditional_thai', 'head_spa','sauna_price',
        'ikitai'
    ]
    make_csv_file(columns=columns) #csvファイルを作成
    sauna_price_dic = {} #サウナ名とサウナの入浴料を格納している辞書型
    #一覧ページからサウナ名と入浴料をスクレイピング
    for i in range(1,sauna_list_page_file_num+1):
        soup = read_html_file(file_path=sauna_list_page_file_path,page_count=i)
        sauna_price_dic = scraping_sauna_price(soup=soup,sauna_price_dic=sauna_price_dic)
    #詳細ページからスクレイピングしてcsvに書き出す
    for i in range(1,sauna_detail_page_file_num+1):
        if os.path.exists('{}/page{}.html'.format(sauna_detail_page_file_path,i)):
            soup = read_html_file(file_path=sauna_detail_page_file_path,page_count=i)
            dic = scraping_detail_page(soup=soup,sauna_price_dic=sauna_price_dic)
            write_csv_file(dic=dic, columns=columns)
            if i % 10 == 0:
                print('{}/{}件スクレイピング完了'.format(i,sauna_detail_page_file_num))
    if sauna_detail_page_file_num % 10 !=0:
        print('{}/{}件スクレイピング完了'.format(sauna_detail_page_file_num,sauna_detail_page_file_num))
if __name__ == '__main__':
    main()