package com.ssafy.api.service;

import com.ssafy.api.request.*;
import com.ssafy.api.response.JejuPlaceRes;
import com.ssafy.api.response.PlaceDetailRes;
import com.ssafy.api.response.ScheduleThumbnailRes;
import com.ssafy.api.response.SearchPlaceRes;
import com.ssafy.db.entity.*;
import com.ssafy.db.repository.*;
import kong.unirest.GenericType;
import kong.unirest.HttpResponse;
import kong.unirest.Unirest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Period;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;

@Service("scheduleService")
@RequiredArgsConstructor
public class ScheduleServiceImpl implements ScheduleService {
    private final UserRepository userRepository;
    private final ScheduleThumbnailRepository scheduleThumbnailRepository;
    private final ScheduleRepository scheduleRepository;
    private final ScheduleItemRepository scheduleItemRepository;
    private final SurveyRepository surveyRepository;
    private final JejuPlaceRepository jejuPlaceRepository;

    @Override
    public List<SearchPlaceRes> getserarchPlace(String keyword) {
        Optional<List<JejuPlace>> oJejuPlacesList = jejuPlaceRepository.findByNameContaining(keyword);
        List<JejuPlace> jejuPlaceList = oJejuPlacesList.orElseThrow(() -> new IllegalArgumentException("검색 결과가 없습니다."));
        List<SearchPlaceRes> serachPlaceResList = new ArrayList<>();

        for(JejuPlace jejuPlace : jejuPlaceList) {
            LinkedHashMap<String, Double> map = new LinkedHashMap<>();
            map.put("La", jejuPlace.getLatitude());
            map.put("Ma", jejuPlace.getLongitude());

            SearchPlaceRes serachPlaceRes = new SearchPlaceRes(
                    serachPlaceResList.size()+1,
                    jejuPlace.getImgUrl(),
                    jejuPlace.getName(),
                    jejuPlace.getRoadAddress(),
                    map);
            serachPlaceResList.add(serachPlaceRes);
        }

        return serachPlaceResList;
    }

    @Override
    public PlaceDetailRes getPlaceDetail(int jejuPlaceId) {
        Optional<JejuPlace> oJejuPlaces = jejuPlaceRepository.findById(jejuPlaceId);
        JejuPlace jejuPlace = oJejuPlaces.orElseThrow(() -> new IllegalArgumentException("jejuPlace doesn't exist"));

        return PlaceDetailRes.builder()
                .placeUrl(jejuPlace.getPlaceUrl())
                .reviewScore((double) (jejuPlace.getReviewScoreSum() / jejuPlace.getReviewCount()))
                .latitude(jejuPlace.getLatitude())
                .longitude(jejuPlace.getLongitude())
                .jejuPlaceName(jejuPlace.getName())
                .roadAddress(jejuPlace.getRoadAddress())
                .build();
    }



    @Override
    public List<ScheduleThumbnailRes> getScheduleThumbnail() {
        List<ScheduleThumbnail> scheduleThumbnailList = scheduleThumbnailRepository.findAll();
        List<ScheduleThumbnailRes> scheduleThumbnailResList = new ArrayList<>();

        for(ScheduleThumbnail scheduleThumbnail : scheduleThumbnailList) {
            ScheduleThumbnailRes scheduleThumbnailRes = ScheduleThumbnailRes.builder()
                    .scheduleThumbnailId(scheduleThumbnail.getId())
                    .thumbnailImageUrl(scheduleThumbnail.getThumbnailImageUrl())
                    .build();
            scheduleThumbnailResList.add(scheduleThumbnailRes);
        }
        return scheduleThumbnailResList;
    }

    @Override
    public void registSchedule(ScheduleRegistReq scheduleRegistReq) {
        Optional<User> oUser = userRepository.findById(scheduleRegistReq.getUserId());
        User user = oUser.orElseThrow(() -> new IllegalArgumentException("user doesn't exist"));

        Optional<Survey> oSurvey = surveyRepository.findById(scheduleRegistReq.getSurveyId());
        Survey survey = oSurvey.orElseThrow(() -> new IllegalArgumentException("survey doesn't exist"));

        int period = Period.between(survey.getStartDate(), survey.getEndDate()).getDays() + 1;

        Optional<ScheduleThumbnail> oScheduleThumbnail = scheduleThumbnailRepository.findById(scheduleRegistReq.getScheduleThumbnailId());
        ScheduleThumbnail scheduleThumbnail = oScheduleThumbnail.orElseThrow(() -> new IllegalArgumentException("scheduleThumbnail doesn't exist"));

        Schedule schedule = Schedule.builder()
                .user(user)
                .survey(survey)
                .scheduleThumbnail(scheduleThumbnail)
                .name(scheduleRegistReq.getName())
                .period(period)
                .isDelete(false)
                .isReview(false)
                .build();

        scheduleRepository.save(schedule);

        List<ScheduleRegistItem> scheduleRegistItemList = scheduleRegistReq.getScheduleRegistItemList();
        for(ScheduleRegistItem scheduleRegistItem : scheduleRegistItemList) {
            Optional<JejuPlace> oJejuPlace = jejuPlaceRepository.findById(scheduleRegistItem.getJejuPlaceId());
            JejuPlace jejuPlace = oJejuPlace.orElseThrow(() -> new IllegalArgumentException("jejuPlace doesn't exist"));

            scheduleRegistItem.getJejuPlaceId();
            ScheduleItem scheduleItem = ScheduleItem.builder()
                    .schedule(schedule)
                    .jejuPlace(jejuPlace)
                    .day(scheduleRegistItem.getDay())
                    .build();

            scheduleItemRepository.save(scheduleItem);
        }
    }

    @Override
    public List<JejuPlaceRes> getRecommendJejuPlace(SurveyRegistReq surveyRegistReq) {
        List<JejuPlace> jejuPlaceList = jejuPlaceRepository.findAll();
        List<FlaskJejuPlaceItem> flaskJejuPlaceItemList = new ArrayList<>();

        for(JejuPlace jejuPlace : jejuPlaceList) {
            FlaskJejuPlaceItem flaskJejuPlaceItem = FlaskJejuPlaceItem.builder()
                    .jejuPlaceId(jejuPlace.getId())
                    .name(jejuPlace.getName())
                    .category(jejuPlace.getCategory().getCategoryName())
                    .categoryDetail(jejuPlace.getCategory().getCategoryDetailName())
                    .latitude(jejuPlace.getLatitude())
                    .longitude(jejuPlace.getLongitude())
                    .reviewScore((double) (jejuPlace.getReviewScoreSum() / jejuPlace.getReviewCount()))
                    .build();

            flaskJejuPlaceItemList.add(flaskJejuPlaceItem);
        }

        FlaskRecommendReq recommendReq = FlaskRecommendReq.builder()
                .surveyRegistReq(surveyRegistReq)
                .flaskJejuPlaceItemList(flaskJejuPlaceItemList)
                .build();

////        Unirest.config().defaultBaseUrl("http://127.0.0.1:5000");
////        HttpResponse<String> result = Unirest.get("/test").asString();
//
////        HttpResponse<String> result = Unirest.get("http://127.0.0.1:5000/test").asObject(recommendReq);
//        List<Integer> list = Unirest.get("http://127.0.0.1:5000/getRecommend").header("survey", recommendReq.toString()).asObject(new GenericType<List<Integer>>() {}).getBody();
//        System.out.println(list.isEmpty());
////        System.out.println(list.size());
////        for(Integer i : list) {
////            System.out.println("i: " + i);
////        }
////        System.out.println("header: " + result.getHeaders());
////        System.out.println("body: " + result.getBody());
////        System.out.println("status: " + result.getStatus());
//
////        String list = result.getBody();
////        List<Integer> jejuRecommendList = Unirest.get("http://127.0.0.1:5000/test")
////                .asObject(new GenericType<List<Integer>>() {})
////                .getBody();

        return null;
    }

}
