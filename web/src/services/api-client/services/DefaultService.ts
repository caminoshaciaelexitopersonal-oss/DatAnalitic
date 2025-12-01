/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatRequest } from '../models/ChatRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DefaultService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Metrics
     * Endpoint that serves Prometheus metrics.
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricsMetricsGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/metrics',
        });
    }
    /**
     * Chat Agent
     * Handles a chat message by invoking the intelligent agent with the
     * message and the context from the current session, following the correct
     * LangChain message structure.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public chatAgentUnifiedV1ChatPost(
        requestBody: ChatRequest,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/unified/v1/chat',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Root
     * @returns any Successful Response
     * @throws ApiError
     */
    public readRootGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/',
        });
    }
    /**
     * Health Check
     * Endpoint for health checks.
     * @returns any Successful Response
     * @throws ApiError
     */
    public healthCheckHealthGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/health',
        });
    }
}
