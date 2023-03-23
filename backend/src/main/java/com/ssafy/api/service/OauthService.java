package com.ssafy.api.service;

import com.nimbusds.oauth2.sdk.AccessTokenResponse;
import com.ssafy.api.request.RefreshTokenRequest;
import com.ssafy.api.response.LoginResponse;
import com.ssafy.api.response.OauthTokenResponse;
import com.ssafy.config.JwtTokenProvider;
import com.ssafy.db.entity.*;
import com.ssafy.db.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.client.WebClient;

import javax.naming.AuthenticationException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class OauthService {

    private static final String BEARER_TYPE = "Bearer";
    private final InMemoryClientRegistrationRepository inMemoryRepository;
    private final UserRepository userRepository;
    private final JwtTokenProvider jwtTokenProvider;
//    private final RedisUtil redisUtil;

    @Transactional
    public LoginResponse login(String providerName, String code) {

        ClientRegistration provider = inMemoryRepository.findByRegistrationId(providerName);
        OauthTokenResponse tokenResponse = getToken(code, provider);
        User user = getUserProfile(providerName,tokenResponse, provider);

        String accessToken = jwtTokenProvider.createAccessToken(String.valueOf(user.getId()));
        String refreshToken = jwtTokenProvider.createRefreshToken();

        return LoginResponse.builder()
                .id(user.getId())
                .name(user.getUserProfile().getNickName())
                .email(user.getEmail())
                .role(user.getRole())
                .tokenType(BEARER_TYPE)
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .build();
    }

    private OauthTokenResponse getToken(String code, ClientRegistration provider) {
        return WebClient.create()
                .post()
                .uri(provider.getProviderDetails().getTokenUri())
                .headers(header -> {
                    header.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
                    header.setAcceptCharset(Collections.singletonList(StandardCharsets.UTF_8));
                })
                .bodyValue(tokenRequest(code, provider))
                .retrieve()
                .bodyToMono(OauthTokenResponse.class)
                .block();
    }

    private MultiValueMap<String, String> tokenRequest(String code, ClientRegistration provider) {
        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("code", code);
        formData.add("grant_type", "authorization_code");
        formData.add("redirect_uri", provider.getRedirectUri());
        formData.add("client_id", provider.getClientId());
        return formData;
    }

    private User getUserProfile(String providerName, OauthTokenResponse tokenResponse, ClientRegistration provider) {
        Map<String, Object> userAttributes = getUserAttributes(provider, tokenResponse);
        Oauth2UserInfo oauth2UserInfo = null;
        if(providerName.equals("kakao")) {
            oauth2UserInfo = new KakaoUserInfo(userAttributes);
        }else{
            log.info("허용되지 않은 접근 입니다.");
        }

        String provide = oauth2UserInfo.getProvider();
        String providerId = oauth2UserInfo.getProviderId();
        String nickName = oauth2UserInfo.getNickName();
        String email = oauth2UserInfo.getEmail();
        LocalDateTime createdDate = oauth2UserInfo.getCreatedDate();

        User userEntity = userRepository.findByEmail(email);

        if (userEntity == null){
            userEntity = User.createUser(email, nickName, createdDate, provide, providerId);
            userRepository.save(userEntity);
        }

        return userEntity;
    }

    private Map<String, Object> getUserAttributes(ClientRegistration provider, OauthTokenResponse tokenResponse) {
        return WebClient.create()
                .get()
                .uri(provider.getProviderDetails().getUserInfoEndpoint().getUri())
                .headers(header -> header.setBearerAuth(tokenResponse.getAccessToken()))
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .block();
    }

    /**
     * refresh Token 으로 Access Token 이 만료 되었을 경우 재발급
     * Redis Server 에서 refresh Token 을 가져옴
     */
//    public AccessTokenResponse accessTokenByRefreshToken(String accessToken, RefreshTokenRequest refreshTokenRequest) {
//        refreshTokenExtractor(refreshTokenRequest);
//        String id = jwtTokenProvider.getPayload(accessToken);
//        String data = redisUtil.getData(id);
//        if (!data.equals(refreshTokenRequest.getRefreshToken())) {
//            log.info("Exception!!");
//            throw new CustomException(ErrorCode.UNAUTHORIZED_REFRESH_TOKEN);
//        }
//
//        Token newAccessToken = jwtTokenProvider.createAccessToken(id);
//
//        return new AccessTokenResponse(newAccessToken.getValue());
//    }

}
