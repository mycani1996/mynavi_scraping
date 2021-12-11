import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import datetime

# 定数を定義
LOG_FILE_PATH = './log/log_{export_at}.log'

# Chromeを起動する関数
def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
        options = ChromeOptions()
    else:
        options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        # return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
        return Chrome(ChromeDriverManager().install(),options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

def write_log(name,log_str):
    now_log = datetime.datetime.now()
    with open(name, mode='a+',encoding="utf_8-sig") as log_file:
        log_file.writelines(f"{str(now_log)}:{str(log_str)}\n")

def get_table_data(elements,word):
    # テーブルの情報取得
    tr_elements = elements.find_elements_by_css_selector('.tableCondition tr')
    td_txt = "不明"
    for tr_elem in tr_elements:
        th_value = tr_elem.find_element_by_tag_name('th').text 
        if th_value == word:
            td_txt = tr_elem.find_element_by_tag_name('td').text
    return td_txt

# main処理
def main():
    search_keyword = input("キーワードを入力：")
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    # 入力されたキーワードのWebサイトを開く
    driver.get("https://tenshoku.mynavi.jp/list/kw"+search_keyword)
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # # 検索窓に入力
    # driver.find_element_by_class_name(
    #     "topSearch__text").send_keys(search_keyword)
    # # 検索ボタンクリック
    # driver.find_element_by_class_name("topSearch__button").click()

    # 検索結果の件数を取得
    content_num = int(driver.find_element_by_css_selector(".result__num em").text)
    print(content_num)

    # Log用/output用のファイル名を用意
    now = datetime.datetime.now()
    log_file_path = LOG_FILE_PATH.format(export_at=now.strftime('%Y%m%d_%H%M%S'))
    out_file_path = './data/out_'+now.strftime('%Y%m%d_%H%M%S') +'_'+search_keyword+'.csv'

    # 空のDataFrame作成
    df = pd.DataFrame()
    i:int
    i=0

    # ページ終了まで繰り返し取得(検索結果件数以下の間実施)
    while 1:
        # 検索結果を全件取得
        content_list = driver.find_elements_by_class_name("cassetteRecruit__content")
        # print(len(content_list))

        # 各企業情報を取得
        for elem in content_list:
            i += 1
            # Logを残す
            write_log(log_file_path,str(i)+"会社目")

            # 会社名取得
            name = elem.find_element_by_class_name('cassetteRecruit__name')
            # 給料と年収情報を取得
            kyuyo = get_table_data(elem,"給与")
            nensyu = get_table_data(elem,"初年度年収")

            # print(name.text)
            # DataFrameに対して辞書形式でデータを追加する
            df = df.append(
                {"会社名": name.text, 
                "給与": kyuyo,
                "初年度年収": nensyu}, 
                ignore_index=True)

        # 次のページへ
        next_page_elem = driver.find_elements_by_xpath("//*[@class='pager__item--active']/following-sibling::li[1]/a")
        if len(next_page_elem) == 0:
            write_log(log_file_path,"最終ページ")
            break
        else:
            driver.get(next_page_elem[0].get_attribute('href'))
            write_log(log_file_path,"ページ遷移")
            time.sleep(3)

    # csv形式で出力
    try:
        df.to_csv(out_file_path,encoding="utf_8-sig")
    except FileNotFoundError:
        write_log(log_file_path,"Output File not found. Make File")
        with open(out_file_path, mode='w') as out_file:
            out_file.write('')
        df.to_csv(out_file_path,encoding="utf_8-sig")
    finally:
        write_log(log_file_path,"finished.")
        driver.close()

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
