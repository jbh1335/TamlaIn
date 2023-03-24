import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
import keyboard
import sys


class PlaceInfoScraper:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(5)

    def get_place_info(self, address):
        self.driver.get(address)
        sleep(2)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        location_evaluation = soup.select("div.location_evaluation > a.link_evaluation")
        comment_count = 0
        review_count = 0
        for ele in location_evaluation:
            if ele["data-target"] == "comment":
                comment_count = int(ele["data-cnt"])
            elif ele["data-target"] == "review":
                review_count = int(ele["data-cnt"])
        return comment_count, review_count

    def get_place_data(self, address):
        result = {}
        self.driver.get(address)
        sleep(2)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 유효한 주소인지 확인
        if soup.select_one("div.wrap_mapdetail.no_result") is not None:
            return None

        # 장소 이미지 url
        img_url = soup.select_one("div.details_present > a.link_present > span.bg_present")
        if img_url is not None:
            img_url = img_url["style"][24:-2]

        # 태그
        link_tag = soup.select("div.location_detail > div.txt_tag > span.tag_g > a.link_tag")
        ar = []
        if link_tag is not None:
            for tag in link_tag:
                ar.append(tag.text[1:])
        tag_df = pd.DataFrame(ar, columns=["tag"])

        # 리뷰
        location_evaluation = soup.select("div.location_evaluation > a.link_evaluation")
        comment_count = 0
        for ele in location_evaluation:
            if ele["data-target"] == "comment":
                comment_count = int(ele["data-cnt"])

        while comment_count > 3:
            button = self.driver.find_element(By.CLASS_NAME, 'link_more')
            sleep(0.5)
            btn_text = button.text

            if btn_text in ["메뉴 더보기", "상품정보 더보기", "코스 더보기"]:
                button = self.driver.find_elements(By.CLASS_NAME, 'link_more')
                sleep(0.5)
                btn_text = button[1].text
                button = button[1]

            if btn_text == "후기 접기":
                break
            button.click()

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        reviews = soup.select("ul.list_evaluation > li")
        created_date = []
        score = []
        for review in reviews:
            time_write = review.select_one("div.unit_info > span.time_write").text
            rating_per = review.select_one("div.star_info > div > span > span")["style"][6:-2]
            user_rating = int(int(rating_per) / 20)  # 유저별 별점
            created_date.append(time_write)
            score.append(user_rating)

        ar = np.array([score, created_date]).T
        review_df = pd.DataFrame(ar, columns=["score", "created_date"])

        result["img_url"] = img_url
        result["tag"] = tag_df
        result["review"] = review_df

        # print(result)
        return result

    def get_road_address(self, address):
        self.driver.get(address)
        sleep(2)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        txt_address = soup.select_one("div.location_detail > span.txt_address")
        road_address = ""
        if txt_address is not None:
            road_address = txt_address.text
            road_address = ' '.join(road_address.split())
            if "(우)" in road_address:
                idx = road_address.index("(우)")
                road_address = road_address[:idx - 1]
        return road_address


def remove_duplicate_place_code(df):
    df = df.drop_duplicates(['place_code'])
    df = df.reset_index()
    return df


def read_pickle_and_split_category():
    df = pd.read_pickle(f'jeju(1).pkl').drop(columns='index')

    for i in range(2, 10):
        df = pd.concat([df, pd.read_pickle(f'jeju({i}).pkl').drop(columns='index')], ignore_index=True)
    print(f"{len(df)}개 데이터를 읽어옴")

    category_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                     {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타", "code": ""}]
    columns_list = ["place_code", "place_name", "category_code", "category_name", "x", "y",
                    "road_address", "place_url"]

    arr_1 = pd.DataFrame(columns=columns_list);
    arr_2 = pd.DataFrame(columns=columns_list);
    arr_3 = pd.DataFrame(columns=columns_list);
    arr_4 = pd.DataFrame(columns=columns_list);
    arr_5 = pd.DataFrame(columns=columns_list);

    for idx, ser in df.iterrows():
        print(idx)
        if ser["category_code"] == category_list[0]["code"]:
            arr_1 = pd.concat([arr_1, ser.to_frame().T], ignore_index=True)
        elif ser["category_code"] == category_list[1]["code"]:
            arr_2 = pd.concat([arr_2, ser.to_frame().T], ignore_index=True)
        elif ser["category_code"] == category_list[2]["code"]:
            arr_3 = pd.concat([arr_3, ser.to_frame().T], ignore_index=True)
        elif ser["category_code"] == category_list[3]["code"]:
            arr_4 = pd.concat([arr_4, ser.to_frame().T], ignore_index=True)
        elif ser["category_code"] == category_list[4]["code"]:
            arr_5 = pd.concat([arr_5, ser.to_frame().T], ignore_index=True)

    arr_1 = remove_duplicate_place_code(arr_1)
    arr_2 = remove_duplicate_place_code(arr_2)
    arr_3 = remove_duplicate_place_code(arr_3)
    arr_4 = remove_duplicate_place_code(arr_4)
    arr_5 = remove_duplicate_place_code(arr_5)

    arr_1.to_pickle('문화시설.pkl')
    arr_2.to_pickle('관광명소.pkl')
    arr_3.to_pickle('음식점.pkl')
    arr_4.to_pickle('카페.pkl')
    arr_5.to_pickle('기타.pkl')

    arr_1.to_excel("문화시설.xlsx")
    arr_2.to_excel("관광명소.xlsx")
    arr_3.to_excel("음식점.xlsx")
    arr_4.to_excel("카페.xlsx")
    arr_5.to_excel("기타.xlsx")

    print(len(arr_1), len(arr_2), len(arr_3), len(arr_4), len(arr_5))


def drop_by_category():
    df = pd.read_pickle(f'기타.pkl').drop(columns='index')
    category_name_list = ["문화,예술 > 미술,공예", "스포츠,레저", "여행 > 관광,명소"]

    for idx, ser in df.iterrows():
        print(idx)
        flag = False
        for i in range(0, len(category_name_list)):
            if category_name_list[i] in ser["category_name"]:
                flag = True
                break
        if flag is False:
            df.drop(idx, inplace=True)

    df.to_pickle('기타(필터링).pkl')
    df.to_excel("기타(필터링).xlsx")


def crawling_review_count(n, start, end):
    print(start, end)
    scraper = PlaceInfoScraper()
    category_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                     {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타(필터링)", "code": ""}]

    comment_count_list = []
    review_count_list = []
    df = pd.read_pickle(f'{category_list[n - 1]["name"]}.pkl')[start:end]
    for idx, ser in df.iterrows():
        url = ser["place_url"]
        comment_count, review_count = scraper.get_place_info(url)
        comment_count_list.append(comment_count)
        review_count_list.append(review_count)
        print(f"{idx + 1}/{len(df)} ({comment_count}, {review_count})     {url}")
    df["comment_count"] = comment_count_list
    df["review_count"] = review_count_list

    df.to_pickle(f'{category_list[n - 1]["name"]}_new_{start}.pkl')
    df.to_excel(f'{category_list[n - 1]["name"]}_new_{start}.xlsx')


def concat_pickle(n):
    category_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                     {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타(필터링)", "code": ""}]

    df = pd.read_pickle(f'{category_list[n - 1]["name"]}_new_0.pkl')
    if 'index' in df.columns:
        df = df.drop(columns='index')

    for i in range(1, 5):
        data = pd.read_pickle(f'{category_list[n - 1]["name"]}_new_{i * 1000}.pkl')
        if 'index' in data.columns:
            data = data.drop(columns='index')
        df = pd.concat([df, data], ignore_index=True)

    df.to_pickle(f'{category_list[n - 1]["name"]}_new.pkl')
    df.to_excel(f'{category_list[n - 1]["name"]}_new.xlsx')


def drop_row_by_review_count(n):
    category_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                     {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타(필터링)", "code": ""}]

    df = pd.read_pickle(f'{category_list[n - 1]["name"]}_new.pkl')
    if 'index' in df.columns:
        df = df.drop(columns='index')
    new_df = pd.DataFrame()
    sum_list = []
    for idx, ser in df.iterrows():
        sum = int(ser["comment_count"]) + int(ser["review_count"])
        if sum == 0:
            continue
        sum_list.append(sum)
        new_df = pd.concat([new_df, ser.to_frame().T], ignore_index=True)
    new_df["sum"] = sum_list

    new_df.to_pickle(f'{category_list[n - 1]["name"]}_nonezero.pkl')
    new_df.to_excel(f'{category_list[n - 1]["name"]}_nonezero.xlsx')


def select_row_by_review_count(n):
    category_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                     {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타(필터링)", "code": ""}]

    df = pd.read_pickle(f'{category_list[n - 1]["name"]}_nonezero.pkl')
    if 'index' in df.columns:
        df = df.drop(columns='index')
    new_df = pd.DataFrame()
    for idx, ser in df.iterrows():
        if int(ser["sum"]) < 10:
            continue
        new_df = pd.concat([new_df, ser.to_frame().T], ignore_index=True)

    new_df.to_pickle(f'{category_list[n - 1]["name"]}_select.pkl')
    new_df.to_excel(f'{category_list[n - 1]["name"]}_select.xlsx')


def count_place_by_category(n):
    category_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                     {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타(필터링)", "code": ""}]
    df = pd.read_pickle(f'{category_list[n - 1]["name"]}_select.pkl')
    category_count_dic = {}
    for idx, ser in df.iterrows():
        category_name = ser["category_name"]
        if category_name in category_count_dic.keys():
            category_count_dic[category_name] = category_count_dic[category_name] + 1
        else:
            category_count_dic[category_name] = 1

    category_count_dic = dict(sorted(category_count_dic.items()))
    for key, value in category_count_dic.items():
        print(key, value)


def separation_by_category_name():
    file_list = [{"name": "문화시설", "code": "CT1"}, {"name": "관광명소", "code": "AT4"},
                 {"name": "음식점", "code": "FD6"}, {"name": "카페", "code": "CE7"}, {"name": "기타(필터링)", "code": ""}]

    df = pd.DataFrame()
    drop_ser = pd.DataFrame()
    category_list = ["맛집", "카페/간식", "액티비티/체험", "스포츠/레저", "전시", "휴양"]
    subcategory_list = [[], [], [], [], [], []]
    subcategory_list[0] = {
        "한식": ["기사식당", "도시락", "한식", "감자탕", "곰탕", "국밥", "국수", "냉면", "두부전문점", "사철탕,영양탕", "설렁탕", "수제비", "순대", "쌈밥",
               "육류,고기", "갈비", "곱창,막창", "꿩,타조", "닭요리", "삼계탕", "불고기,두루치기", "삼겹살", "오리", "족발,보쌈", "주먹밥", "죽", "찌개,전골",
               "한정식", "해물,생선", "게,대게", "굴,전복", "매운탕,해물탕", "복어", "아구", "장어", "조개", "추어", "회", "해장국"],
        "일식": ["일식", "돈까스,우동", "일본식라면", "일식집", "참치회", "초밥,롤", "철판요리"],
        "중식": ["중식", "양꼬치", "중국요리"],
        "분식": ["분식", "떡볶이"],
        "양식": ["샐러드", "양식", "멕시칸,브라질", "스테이크,립", "이탈리안", "피자", "해산물", "바닷가재", "햄버거", "패스트푸드", "샌드위치"],
        "술집": ["술집", "실내포장마차", "와인바", "일본식주점", "칵테일바", "호프,요리주점"],
        "아시아": ["아시아음식", "동남아음식", "베트남음식", "태국음식", "인도음식", "터키음식"],
        "뷔페/레스토랑": ["뷔페", "고기뷔페", "한식뷔페", "해산물뷔페", "패밀리레스토랑"],
        "샤브샤브": ["샤브샤브"],
        "치킨": ["치킨"],
        "퓨전": ["퓨전요리", "퓨전일식", "퓨전중식", "퓨전한식"]}
    subcategory_list[1] = {
        "카페": ["카페", "공차", "다방", "생과일전문점", "리치망고", "쥬씨", "전통찻집", "오가다", "커피전문점", "달리는커피", "드롭탑", "메가MGC커피", "블루샥",
               "빽다방", "스타벅스", "엔제리너스", "읍천리382", "이디야커피", "커피빈", "컴포즈커피", "탐앤탐스", "투썸플레이스", "파스쿠찌", "폴바셋", "할리스",
               "팔공티"],
        "디저트": ["간식", "닭강정", "도넛", "떡,한과", "아이스크림", "제과,베이커리", "초콜릿", "디저트카페", "디저트39", "설빙"],
        "이색카페": ["테마카페", "갤러리카페", "고양이카페", "만화카페", "놀숲", "벌툰", "북카페", "애견카페", "키즈카페"]}
    subcategory_list[2] = {"승마": ["승마", "승마장"],
                           "관광농원": ["관광농원"],
                           "동물원": ["동물원", "실내동물원"],
                           "유원지/민속촌": ["유원지", "민속촌"],
                           "테마체험": ["테마파크", "카페거리", "워터테마파크", "테마거리", "먹자골목", "도자기,도예촌", "미술,공예", "도자기", "목공예", "수예,자수",
                                    "화랑", "화방"],
                           "과학": ["과학관", "천문대"]}
    subcategory_list[3] = {"골프": ["골프장"],
                           "해양": ["낚시", "낚시터", "수영,수상", "수상스포츠", "스킨스쿠버"],
                           "자전거/싸이클": ["스포츠,레저", "자전거,싸이클", "자전거대여소"]}
    subcategory_list[4] = {"박물관": ["박물관", "테디베어뮤지엄"],
                           "미술관": ["미술관"],
                           "전시관": ["전시관"],
                           "문화유적": ["문화유적", "릉,묘,총", "봉수대", "사당,제단", "산성,성곽", "생가,고택", "유적지", "탑,비석", "향교,서당", "종교유적지"],
                           "기념관": ["기념관"],
                           "공연/연극": ["공연장,연극극장"]}
    subcategory_list[5] = {"산": ["산", "산봉우리", "등산로"],
                           "오름": ["오름"],
                           "올레길": ["제주올레길"],
                           "해변": ["해수욕장,해변", "방조제", "바위"],
                           "자연생태": ["저수지", "호수", "계곡", "동굴", "연못", "폭포", "하천"],
                           "도보": ["도보여행", "숲", "둘레길", "자연휴양림", "고개", "촬영지"],
                           "수목원/식물원": ["수목원,식물원"],
                           "섬": ["섬"],
                           "공원": ["도립공원", "국립공원"],
                           "온천": ["온천"],
                           }

    exception_category_name = ["음식점", "관광,명소", "생태보존,서식지"]
    subcategory_by_place_name = {"이령": "한식",
                                 "와인도시": "양식",
                                 "광명대창집 신서귀포점": "한식",
                                 "텐더로인": "일식",
                                 "싱싱식당": "중식",
                                 "생이기정": "도보",
                                 "도구리알": "해변",
                                 "월령코지": "해변",
                                 "산양큰엉곶": "도보",
                                 "저지예술인마을": "도보",
                                 "한담해안산책로": "도보",
                                 "제주탐나라공화국": "테마체험",
                                 "화순곶자왈": "도보",
                                 "박수기정": "해변",
                                 "어음리억새군락지": "도보",
                                 "돌염전": "해변",
                                 "갯깍주상절리대": "해변",
                                 "진곶내 (폐쇄)": "해변",
                                 "선녀코지": "해변",
                                 "한라산영실": "산",
                                 "메밀꽃밭": "도보",
                                 "법환어촌계해녀체험센터": "테마체험",
                                 "속골": "자연생태",
                                 "돔베낭골": "해변",
                                 "황우지선녀탕": "해변",
                                 "동너븐덕": "해변",
                                 "소남머리": "공원",
                                 "정모시쉼터": "도보",
                                 "소천지": "자연생태",
                                 "생이돌": "해변",
                                 "닭머르": "해변",
                                 "김경숙해바라기농장": "관광농원",
                                 "조천만세동산": "공원",
                                 "관곶": "해변",
                                 "서우봉 일몰지": "해변",
                                 "위미리수국길": "도보",
                                 "태웃개": "해변",
                                 "올티스": "테마체험",
                                 "동복관광체험어장": "테마체험",
                                 "유채꽃프라자": "도보",
                                 "가시리 국산화 풍력발전단지": "도보",
                                 "제주동백마을": "도보",
                                 "김녕금속공예벽화마을": "도보",
                                 "청굴물": "해변",
                                 "송당무끈모루": "도보",
                                 "오저여": "해변",
                                 "짱구네 유채꽃밭": "도보",
                                 "유채꽃밭": "도보",
                                 "비양도망대": "해변",
                                 "청수곶자왈": "도보",
                                 "납읍난대림지역": "도보",
                                 "1100고지습지": "산",
                                 "제주농업생태원": "테마체험",
                                 "하도리철새도래지": "해변"
                                 }
    category_col = []
    subcategory_col = []
    # 5개 파일 읽어오면서 반복
    for i in range(0, len(file_list)):
        temp_df = pd.read_pickle(f'{file_list[i]["name"]}_select.pkl')
        # print(file_list[i]["name"])
        # print(temp_df)
        # 각 파일의 row 마다 category_name을 이용하여 카테고리 분류
        for idx, ser in temp_df.iterrows():
            find = False
            name = ser["category_name"].split(' > ')[-1]
            if name in exception_category_name:
                place_name = ser["place_name"]
                if place_name in subcategory_by_place_name.keys():
                    subcategory = subcategory_by_place_name[place_name]
                    for j in range(0, len(subcategory_list)):
                        if subcategory in subcategory_list[j].keys():
                            find = True
                            category_col.append(category_list[j])
                            subcategory_col.append(subcategory)
                            df = pd.concat([df, ser.to_frame().T], ignore_index=True)
            else:
                for j in range(0, len(subcategory_list)):
                    for key, value_list in subcategory_list[j].items():
                        for value in value_list:
                            if value == name:
                                find = True
                                category_col.append(category_list[j])
                                subcategory_col.append(key)
                                df = pd.concat([df, ser.to_frame().T], ignore_index=True)
            if find is False:
                drop_ser = pd.concat([drop_ser, ser.to_frame().T], ignore_index=True)

    df["category"] = category_col
    df["subcategory"] = subcategory_col

    df.to_pickle(f'전체_subcategory.pkl')
    df.to_excel(f'전체_subcategory.xlsx')
    drop_ser.to_pickle(f'drop_subcategory.pkl')
    drop_ser.to_excel(f'drop_subcategory.xlsx')

    print(df)
    print(temp_df)


def print_subcategory_count():
    df = pd.read_pickle('전체_subcategory.pkl')
    count = {"맛집": {}, "카페/간식": {}, "액티비티/체험": {}, "스포츠/레저": {}, "전시": {}, "휴양": {}}
    for idx, ser in df.iterrows():
        category = ser["category"]
        subcategory = ser["subcategory"]
        if subcategory in count[category].keys():
            count[category][subcategory] = count[category][subcategory] + 1
        else:
            count[category][subcategory] = 1
    for category in count.keys():
        print(category)
        sub_dic = dict(sorted(count[category].items()))
        for key, value in sub_dic.items():
            print(key, value)
        print()


def crawling_place_data():
    scraper = PlaceInfoScraper()
    df_file = pd.read_pickle('전체_subcategory.pkl')
    # for x in range(0, 1):
    #     df = df_file[523:524]
    #     i = "temp"
    for i in range(85, 88):
        df = df_file[i * 100:(i + 1) * 100]
        info = pd.DataFrame()
        tag = pd.DataFrame(columns=["place_code", "tag"])
        review = pd.DataFrame(columns=["place_code", "score", "created_date"])
        img_url = []
        tag_count = []

        for idx, ser in df.iterrows():
            url = ser["place_url"]
            code = ser["place_code"]
            data = scraper.get_place_data(url)
            if data is None:
                continue

            # 태그
            data["tag"]["place_code"] = code
            tag = pd.concat([tag, data["tag"]], ignore_index=True)
            tag_count.append(data["tag"].shape[0])
            # 리뷰
            data["review"]["place_code"] = code
            review = pd.concat([review, data["review"]], ignore_index=True)
            # 이미지
            info = pd.concat([info, ser.to_frame().T], ignore_index=True)
            img_url.append(data["img_url"])
            print(
                f"[{i}] {idx}/{df_file.shape[0]} {url} 리뷰 {data['review'].shape[0]}개, 태그 {data['tag'].shape[0]}개, 이미지 {data['img_url']}")

        info["img_url"] = img_url
        info["tag_count"] = tag_count

        # print(info)
        info.to_pickle(f'전체_info_{i}.pkl')
        info.to_excel(f'전체_info_{i}.xlsx')
        # print(tag)
        tag.to_pickle(f'전체_tag_{i}.pkl')
        tag.to_excel(f'전체_tag_{i}.xlsx')
        # print(review)
        review.to_pickle(f'전체_review_{i}.pkl')
        review.to_excel(f'전체_review_{i}.xlsx')


def concat_pickle_file():
    for file_name in ["info", "tag", "review"]:
        new_df = pd.DataFrame()
        for i in range(0, 88):
            df = pd.read_pickle(f'전체_{file_name}_{i}.pkl')
            if 'index' in df.columns:
                df = df.drop(columns='index')
            for idx, ser in df.iterrows():
                new_df = pd.concat([new_df, ser.to_frame().T], ignore_index=True)

            new_df.to_pickle(f'전체_{file_name}.pkl')
            new_df.to_excel(f'전체_{file_name}.xlsx')


def print_tag_count():
    df = pd.read_pickle(f'전체_tag.pkl')
    tag_count_dic = {}
    for idx, ser in df.iterrows():
        tag = ser["tag"]
        if tag in tag_count_dic.keys():
            tag_count_dic[tag] = tag_count_dic[tag] + 1
        else:
            tag_count_dic[tag] = 1

    tag_count_dic = dict(sorted(tag_count_dic.items(), key=lambda item: item[1], reverse=True))
    for key, value in tag_count_dic.items():
        print(f'"{key}",')
    return tag_count_dic


def drop_and_rename_tag():
    info_df = pd.read_pickle(f'전체_info.pkl')
    tag_df = pd.read_pickle(f'전체_tag.pkl')
    tag_dic = {
        "오션뷰": ["바다뷰"],
        "핸드드립": [],
        "브런치": [],
        "일출": [],
        "포토존": ["포토스팟"],
        "빈티지": [],
        "베이커리": [],
        "아이와함께": ["아이와", "어린이"],
        "애견동반": ["동물동반"],
        "루프탑": [],
        "나들이": [],
        "테라스": [],
        "흑돼지": [],
        "서핑": [],
        "고기국수": [],
        "비건": [],
        "갈치조림": [],
        "수제버거": [],
        "승마": [],
        "소금빵": [],
        "귤체험": [],
        "애견카페": [],
        "요트": [],
        "분위기좋은": [],
        "데이트": [],
        "이국적인": [],
        "노포": [],
        "건강식": [],
        "억새밭": [],
        "노키즈존": [],
        "북카페": [],
        "경양식": [],
        "로컬푸드": [],
        "한식뷔페": [],
        "벚꽃": [],
        "원데이클래스": [],
        "대형카페": [],
        "낭만적인": [],
        "레트로풍": [],
        "걷기좋은": [],
        "단풍": [],
        "서핑": [],
        "핑크뮬리": [],
        "노펫존": [],
        "식물카페": [],
        "미디어아트": [],
        "녹차밭": [],
        "회전초밥": [],
        "캠핑느낌나는": [],
        "파스타": [],
        "전망좋은": [],
        "무인카페": [],
        "민속주점": [],
        "플라워카페": [],
        "보드게임카페": [],
        "아기자기한": [],
        "한옥스타일": [],
        "공방": [],
        "유람선": [],
        "트릭아트": [],
        "락카페": [],
        "고등어회": [],
        "프랑스음식": [],
        "드로잉카페": [],
        "이자카야": [],
        "샌드위치": [],
        "지중해요리": [],
        "떡카페": [],
        "이색술집": [],
        "멕시코요리": [],
        "혼고기": [],
        "포토카페": [],
        "한옥카페": [],
        "고양이카페": [],
        "스노클링": [],
        "동백꽃": [],
        "레일바이크": [],
        "몸국": [],
        "스페인요리": [],
        "고즈넉한": [],
        "위스키": [],
        "온실카페": [],
        "룸카페": [],
        "야외카페": [],
        "주택개조카페": [],
        "카약": [],
        "스쿠버다이빙": [],
        "VR체험": [],
        "제주4.3": [],
        "딱새우": [],
        "스테이크": [],
        "샐러드카페": [],
        "북해도식": [],
        "라운지카페": [],
        "만화카페": [],
        "패들보드": [],
        "가족여행": [],
        "수국": [],
        "스누피가든": [],
        "보말칼국수": [],
        "돔베고기": [],
        "오마카세": [],
        "트램폴린카페": [],
        "자전거테마카페": [],
        "족욕카페": [],
        "목공체험": [],
        "보트투어": [],
        "로봇": [],
        "유리공예": [],
        "오페라공연": [],
        "체험미술": [],
        "뮤지컬공연": [],
        "이색박물관": [],
        "아쿠아리움": [],
        "키즈카페": [],
        "힐링": [],
        "노천온천": [],
        "귤따기체험": [],
        "와인카페": [],
        "페러세일링": [],
        "이색체험": [],
        "스쿠버다이빙": [],
        "스킨스쿠버": [],
        "패러글라이딩": [],
        "역사문화관": [],
        "서예체험": [],
        "코끼리": [],
        "카트": [],
    }

    # for i in tag_dic.keys():
    #     for j in tag_dic.keys():
    #         if i != j and i in j:
    #             print(i, "in", j)

    tag_df = pd.read_pickle(f'전체_tag.pkl')
    info_df = pd.read_pickle(f'전체_info.pkl')
    re_tag = {}
    # print(file_list[i]["name"])
    # print(temp_df)
    # 각 파일의 row 마다 category_name을 이용하여 카테고리 분류
    for idx, ser in tag_df.iterrows():
        code = ser["place_code"]
        tag = ser["tag"]
        for name, rename_list in tag_dic.items():
            if tag in rename_list:
                tag = name
            if tag == name:
                if code in re_tag.keys():
                    re_tag[code].add(tag)
                else:
                    re_tag[code] = set([tag])

    for idx, ser in info_df.iterrows():
        subcategory = ser["category_name"].split(' > ')[-1]
        code = ser["place_code"]
        if subcategory == "낚시터":
            subcategory = "낚시"
        elif subcategory == "도자기,도예촌":
            subcategory = "도자기"
        elif subcategory == "스테이크,립":
            subcategory = "스테이크"
        elif subcategory == "회전초밥":
            subcategory = "초밥"
        elif subcategory in ["테마카페", "한식", "일식", "중식", "분식", "양식", "술집", "호프,요리주점", "아시아음식", "뷔페", "패밀리레스토랑", "샤브샤브",
                             "치킨", "퓨전요리", "카페", "공차", "다방", "생과일전문점", "리치망고", "쥬씨", "오가다", "커피전문점", "달리는커피", "드롭탑",
                             "메가MGC커피", "블루샥", "빽다방", "스타벅스", "엔제리너스", "읍천리382", "이디야커피", "커피빈", "컴포즈커피", "탐앤탐스",
                             "투썸플레이스", "파스쿠찌", "폴바셋", "할리스", "팔공티", "간식", "디저트카페", "디저트39", "설빙", "놀숲", "벌툰",
                             "승마", "승마장", "관광농원", "동물원", "실내동물원", "유원지", "민속촌", "미술,공예", "과학관", "천문대",
                             "골프장", "스포츠,레저", "자전거,싸이클", "박물관", "테디베어뮤지엄", "미술관", "전시관", "문화유적", "기념관", "공연장,연극극장", "산",
                             "오름", "제주올레길", "해수욕장,해변", "도보여행", "촬영지", "수목원,식물원", "섬", "도립공원", "국립공원", "온천",
                             "음식점", "관광,명소", "멕시칸,브라질", "혼고기", "일식집", "수영,수상", "유적지", "종교유적지",
                             "테마파크", "카페거리", "워터테마파크", "테마거리", "먹자골목", "수상스포츠", "산책로", "숲", "중국요리",
                             "해물,생선", "해산물", "육류,고기", "돈까스,우동", "일본식주점", "일본식라면", "이탈리안", "국수", "와인바", "칵테일바", "갤러리카페",
                             "둘레길", "자연휴양림"]:
            continue
        if ',' in subcategory:
            subcategory = subcategory.replace(',', '/')
        if code in re_tag.keys():
            re_tag[code].add(subcategory)
        else:
            re_tag[code] = set([subcategory])

    re_tag["12979413"].remove("아이와함께")
    re_tag["8641860"].remove("녹차밭")
    re_tag["14499072"].remove("패들보드")

    tag_df = pd.DataFrame(columns=["place_code", "tag"])
    for code, tag_set in re_tag.items():
        temp_df = pd.DataFrame(list(tag_set), columns=["tag"])
        temp_df["place_code"] = code
        tag_df = pd.concat([tag_df, temp_df], ignore_index=True)

    tag_df.to_pickle(f'전체_tag_new.pkl')
    tag_df.to_excel(f'전체_tag_new.xlsx')


def concat_info_tag_review():
    info_df = pd.read_pickle(f'전체_info.pkl').drop(columns='comment_count').drop(columns='tag_count')

    tag_df = pd.read_pickle(f'전체_tag_new.pkl')
    review_df = pd.read_pickle(f'전체_review.pkl')

    tag_dic = {}
    review_sum_dic = {}
    review_count_dic = {}

    for idx, ser in tag_df.iterrows():
        code = ser["place_code"]
        tag = ser["tag"]
        if code in tag_dic.keys():
            tag_dic[code].append(tag)
        else:
            tag_dic[code] = [tag]

    for idx, ser in review_df.iterrows():
        code = ser["place_code"]
        score = int(ser["score"])
        if code in review_sum_dic.keys():
            review_sum_dic[code] += score
            review_count_dic[code] += 1
        else:
            review_sum_dic[code] = score
            review_count_dic[code] = 1

    comment_count = []
    comment_sum = []
    tag_count = []
    tag = []
    for idx, ser in info_df.iterrows():
        code = ser["place_code"]
        temp_comment_count = 0
        temp_comment_sum = 0
        temp_tag_count = 0
        temp_tag = ""
        if code in tag_dic.keys():
            temp_tag_count = len(tag_dic[code])
            temp_tag = '_'.join(sorted(tag_dic[code]))
        if code in review_sum_dic.keys():
            temp_comment_count = review_count_dic[code]
            temp_comment_sum = review_sum_dic[code]

        comment_count.append(temp_comment_count)
        comment_sum.append(temp_comment_sum)
        tag_count.append(temp_tag_count)
        tag.append(temp_tag)

    info_df["comment_count"] = comment_count
    info_df["comment_sum"] = comment_sum
    info_df["tag_count"] = tag_count
    info_df["tag"] = tag

    info_df.to_pickle(f'전체_info_new.pkl')
    info_df.to_excel(f'전체_info_new.xlsx')


def save_road_address():
    scraper = PlaceInfoScraper()
    df = pd.read_pickle(f'전체_info_new.pkl')
    for idx, ser in df.iterrows():
        road_address = ser["road_address"]
        url = ser["place_url"]
        if road_address == "":
            print(url)
            road_address = scraper.get_road_address(url)
            print(road_address)
            df.loc[idx, 'road_address'] = road_address

    df.to_pickle(f'전체_info_new_notnull.pkl')
    df.to_excel(f'전체_info_new_notnull.xlsx')


def convert_csv():
    df = pd.read_pickle(f'전체_info_new_notnull.pkl')
    df = df.drop(columns=['place_code', "category_code", "category_name", "review_count", "sum", "tag_count"])
    df.rename(columns={'place_name': 'name', "x": "longitude", "y": "latitude", "comment_count": "review_count",
                       "comment_sum": "review_score_sum"}, inplace=True)

    # category, subcategory
    subcategory_list = [
        "분식",
        "뷔페/레스토랑",
        "샤브샤브",
        "술집",
        "아시아",
        "양식",
        "일식",
        "중식",
        "치킨",
        "퓨전",
        "한식",
        "디저트",
        "이색카페",
        "카페",
        "과학",
        "관광농원",
        "동물원",
        "승마",
        "유원지/민속촌",
        "테마체험",
        "골프",
        "자전거/싸이클",
        "해양",
        "공연/연극",
        "기념관",
        "문화유적",
        "미술관",
        "박물관",
        "전시관",
        "공원",
        "도보",
        "산",
        "섬",
        "수목원/식물원",
        "오름",
        "온천",
        "올레길",
        "자연생태",
        "해변"
    ]
    category_pk = []
    for idx, ser in df.iterrows():
        subcategory = ser["subcategory"]
        pk = subcategory_list.index(subcategory) + 1
        category_pk.append(pk)
    df = df.drop(columns=['category', "subcategory"])
    df["category_id"] = category_pk

    df.to_pickle(f'jeju_place.pkl')
    df.to_excel(f'jeju_place.xlsx')
    df.to_csv("jeju_place.csv", encoding='utf-8-sig')


def find_place_pk():
    df = pd.read_pickle(f'jeju_place.pkl')
    while True:
        name = input("장소 이름 : ")
        place_pk = df.index[df['name'] == name].tolist()
        if len(place_pk) == 1:
            place_pk = place_pk[0] + 1
            print(place_pk)
        else:
            print("--------------다시 입력하세요")
            continue



if __name__ == "__main__":
    find_place_pk()
