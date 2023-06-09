package com.ssafy.api.controller.auth;

import com.ssafy.api.service.AuthService;
import com.ssafy.api.controller.auth.util.AuthorizationExtractor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.http.HttpMethod;
import org.springframework.web.servlet.HandlerInterceptor;

public class AuthenticationInterceptor implements HandlerInterceptor {
    private final AuthService authService;

    public AuthenticationInterceptor(AuthService authService) {
        this.authService = authService;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        if (isPreflight(request) || isGet(request)) {
            return true;
        }
        if (!validatesToken(request)) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized");
            return false;
        }
        return true;
    }

    protected boolean validatesToken(HttpServletRequest request) {
        String accessToken = AuthorizationExtractor.extract(request);
        return authService.validatesAccessToken(accessToken);
    }
    protected boolean isPreflight(HttpServletRequest request) {
        return HttpMethod.OPTIONS.matches(request.getMethod());
    }

    protected boolean isGet(HttpServletRequest request) {
        return HttpMethod.GET.matches(request.getMethod());
    }
}