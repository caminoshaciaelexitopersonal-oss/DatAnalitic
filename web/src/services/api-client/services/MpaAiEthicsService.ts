/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BiasAuditRequest } from '../models/BiasAuditRequest';
import type { ModelCardRequest } from '../models/ModelCardRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaAiEthicsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Run Bias Audit
     * Performs a bias audit on a specified model run.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public runBiasAuditUnifiedV1MpaEthicsBiasAuditPost(
        requestBody: BiasAuditRequest,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
    public generateModelCardUnifiedV1MpaEthicsModelCardPost(
        requestBody: ModelCardRequest,
    ): CancelablePromise<string> {
        return this.httpRequest.request({
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
