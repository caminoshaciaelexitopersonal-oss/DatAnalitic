/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaDtlService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Quality Report
     * Retrieves the data quality report for a given job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getQualityReportUnifiedV1MpaDtlJobJobIdQualityGet(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/mpa/dtl/job/{job_id}/quality',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Schema Metadata
     * Retrieves the schema validation metadata for a given job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getSchemaMetadataUnifiedV1MpaDtlJobJobIdSchemaGet(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/mpa/dtl/job/{job_id}/schema',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
