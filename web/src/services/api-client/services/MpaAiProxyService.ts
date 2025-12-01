/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GeminiProxyRequest } from '../models/GeminiProxyRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaAiProxyService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Gemini Proxy
     * Secure proxy endpoint to interact with the Gemini API.
     * The API key is handled on the server-side.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public geminiProxyUnifiedV1MpaAiProxyProxyGeminiPost(
        requestBody: GeminiProxyRequest,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
