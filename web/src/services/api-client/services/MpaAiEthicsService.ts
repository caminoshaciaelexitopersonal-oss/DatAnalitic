/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BiasAuditRequest } from '../models/BiasAuditRequest';
import type { ModelCardRequest } from '../models/ModelCardRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MpaAiEthicsService {
    /**
     * Run Bias Audit
     * Performs a bias audit on a specified model run.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static runBiasAuditUnifiedV1MpaEthicsBiasAuditPost(
        requestBody: BiasAuditRequest,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mpa/ethics/bias-audit',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Generate Model Card
     * Generates and saves a Model Card for a specified model run.
     * @param requestBody
     * @returns string Successful Response
     * @throws ApiError
     */
    public static generateModelCardUnifiedV1MpaEthicsModelCardPost(
        requestBody: ModelCardRequest,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mpa/ethics/model-card',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
