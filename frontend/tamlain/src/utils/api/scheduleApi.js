import client from "../client";

// 장소 아이디 입력 시 해당 장소의 상세 정보
export const getPlaceDetail = async (accessToken, jejuPlaceId) => {
  const response = await client.get(`/schedule/${jejuPlaceId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
};

// 설문 조사를 통한 추천 장소 불러오기
export const getRecommendJejuPlace = async (accessToken, surveyId) => {
  const response = await client.get(`/schedule/recommend/survey/${surveyId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
};

// 재추천하기
export const reloadRecommendJejuPlace = async (accessToken, data) => {
  const response = await client.post(`/schedule/recommend/reload`, data, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
};

// 사용자가 만든 일정 등록하기
export const registSchedule = async (accessToken, data) => {
  const response = await client.post(`/schedule/regist`, data, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
};

// 장소 입력 시 검색하기
export const searchPlace = async (accessToken, keyword) => {
  const response = await client.get(`/schedule/search/${keyword}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
};

// 일정 등록할 썸네일 사진 조회하기
export const getScheduleThumbnail = async (accessToken) => {
  const response = await client.get(`/schedule/thumbnail`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
};
