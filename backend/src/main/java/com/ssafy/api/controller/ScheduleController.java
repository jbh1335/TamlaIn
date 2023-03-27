package com.ssafy.api.controller;

import com.ssafy.api.response.ScheduleThumbnailRes;
import com.ssafy.api.service.ScheduleService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Api(value = "일정 API", tags = {"Schedule"})
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/schedule")
public class ScheduleController {
    private final ScheduleService scheduleService;

    @ApiOperation(value = "일정 썸네일 사진 조회", notes = "일정 등록할 썸네일 사진 조회하기")
    @GetMapping("/thumbnail")
    public ResponseEntity<?> getScheduleThumbnail() {
        List<ScheduleThumbnailRes> scheduleThumbnailResList = scheduleService.getScheduleThumbnail();
        return ResponseEntity.status(200).body(scheduleThumbnailResList);
    }


}
