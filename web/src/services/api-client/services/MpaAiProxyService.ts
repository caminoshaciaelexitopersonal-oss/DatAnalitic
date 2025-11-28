/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GeminiProxyRequest } from '../models/GeminiProxyRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MpaAiProxyService {
    /**
     * Gemini Proxy
     * Secure proxy endpoint to interact with the Gemini API.
     * The API key is handled on the server-side.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static geminiProxyUnifiedV1MpaAiProxyProxyGeminiPost(
        requestBody: GeminiProxyRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mpa/ai_proxy/proxy/gemini',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
