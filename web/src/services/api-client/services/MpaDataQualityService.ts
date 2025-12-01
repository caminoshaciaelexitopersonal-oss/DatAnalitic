/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionRequest } from '../models/SessionRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaDataQualityService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Quality Report
     * Generates a comprehensive data quality report for the dataset associated
     * with the given session_id.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public getQualityReport(
        requestBody: SessionRequest,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
