![image](/docs/MainLogoBlack.png)

# 프로젝트 진행 기간

---

2023.02.20 - 2023.04.07 

SSAFY 8기 2학기 특화프로젝트

# TAMLA:IN - 배경

---

막상 제주도로 여행을 가려 하였지만 계획을 세우긴 싫을 때가 있나요 ? 

제주도 평균 여행기간은 4.2일로 짧지 않은 여행이기에 계획을 세우고 떠나는 분들이 많을껍니다.

인터넷 검색을 하곤 했지만 너무 많은 정보와 나에게 맞춰지지 않은 정보에 힘든 적이 있나요? 


Tamla:In은 그러한 니즈를 충족시켜주기 위해 사용자에게 **맞춰진** 제주 여행지 추천 홈페이지입니다. 

TamIa:In과 함께라면 여행 계획을 세우는 데에 훨씬 간편해집니다!

# 주요 기능

---

## 추천 서비스

- **첫 추천**
    - 사용자에게 설문을 받아 맞춤 장소들을 추천해줍니다.
    - 리뷰, 설문 등을 기반으로 추천을 해줍니다.
    - 해당하는 장소들에 대한 평점을 볼 수 있습니다.
    - 마음에 들지 않는 장소는 삭제할 수 있습니다.
    - 일정을 등록을 하여 일정 목록에 추가할 수 있습니다.
- **재추천**
    - 추천을 받은 장소들을 보다 마음에 들지 않거나 더 많은 장소들을 보고 싶으면 삭제된 장소들과 일정에 추가된 장소들을 받아 재추천해줍니다.

## 일정 작성

- 마음에 드는 장소를 선택하면 지도에 돌하르방 마커로 표시가 되며 일정 목록에 추가가 됩니다.
- 일정을 등록하다가 잘못 넣으면 삭제하고 다시 넣을 수 있습니다.

## 별점 주기

- 방문한 장소에만 별점을 줄 수가 있어요.
- 기간이 지나야만 별점을 줄 수가 있지요.
- 해당 장소들의 별점은 나중에 설문에 영향을 줍니다.

# 주요 기술

---

### DevOps

- Docker : 23.0.1
- Jenkins : 2.387.1
- Gitlab

### DataBase

- Mysql : 8.0.32
- Redis : 5.0.7

### BackEnd

- Java SDK : 11.0.18
- SpringBoot : 2.7.8
- Flask : 2.2.3
- Pandas
- Jwt + OAuth

### FrontEnd

- NodeJs : 16.13.0
- React
- JavaScript

# 프로젝트 파일 구조

---

## BackEnd

```
api
├───main
│   ├───java
│   │   └───com
│   │       └───ssafy
│   │           ├───api
│   │           │   ├───controller
│   │           │   ├───request
│   │           │   ├───response
│   │           │   └───service
│   │           ├───config
│   │           ├───db
│   │           │   ├───entity
│   │           │   └───repository
│   │           ├───exception
│   │           └───util
│   └───resources
└───test
    └───java
        └───com
            └───ssafy
```

## FrontEnd

```
src
├───components
│   ├───Login
│   ├───MainPage
│   ├───MyPage
│   │   ├───History
│   │   └───Star
│   ├───Schedule
│   │   └───Search
│   └───Survey
├───store
├───UI
│   ├───Button
│   ├───FilterBox
│   ├───Frame
│   ├───Input
│   ├───Loading
│   ├───Modal
│   ├───Navbar
│   └───ScrollToTop
└───utils
    └───api
```

# 팀 소개

---

![image](/docs/팀소개.jpg)

# 프로젝트 산출물

---

- [기능명세서](/docs/기능_명세서.pdf)
- [와이어프레임](https://www.figma.com/file/W7ArwvyoHpdOmr6cK7XlrR/%ED%95%A0%EB%A7%9D-%EB%91%98%2C-%ED%95%98%EB%A5%B4%EB%B0%A9-%EB%84%B7?node-id=0-1)
- [API](/docs/API_설계서.pdf)
- [ERD](/docs/erd.png)
- [회의록](/docs/아키텍쳐 설계.png)

# TAMLA:IN - 서비스 화면

---

## 메인 페이지

- 메인 페이지
- 카카오 로그인

    ![image](/docs/메인 페이지, 로그인.gif)

## 설문조사

- 최대 4박 5일 가능하며
- 다양한 카테고리로 사용자 맞춤 서비스 제공

    ![image](/docs/설문조사.gif)

## 일정 등록

- 선택한 장소들이 지도에 마커로 찍이며
- 일차가 다르면 같은 장소 중복으로 가능합니다.
- 장소가 마음에 들지 않으면 삭제가 가능합니다.
- 이미지선택과 일정명 작성 후 등록이 가능합니다.

    ![image](/docs/일정등록.gif)

## 리뷰 등록

- 갔다 온 장소들에 대한 별점을 줄 수 있습니다.
- 방문하지 않은 곳은 미방문 클릭을 해주면 반영이 되지 않습니다.
- 한번 등록하면 다시 등록 할 수 없습니다.

    ![image](/docs/리뷰.gif)

## 마이페이지

- 등록한 일정들이 모여있습니다.

    ![image](/docs/마이페이지.gif)


---
