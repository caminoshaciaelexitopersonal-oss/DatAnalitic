/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionRequest } from '../models/SessionRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MpaDataQualityService {
    /**
     * Get Quality Report
     * Generates a comprehensive data quality report for the dataset associated
     * with the given session_id.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getQualityReportUnifiedV1MpaQualityReportPost(
        requestBody: SessionRequest,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mpa/quality/report',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
