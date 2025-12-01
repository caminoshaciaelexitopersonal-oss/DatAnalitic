/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WpaAutomatedAnalysisService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get All Job Statuses
     * Returns the status of all jobs.
     * @returns any Successful Response
     * @throws ApiError
     */
    public getAllJobStatuses(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/jobs/status',
        });
    }
    /**
     * Get Job Status
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getJobStatus(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/status',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Report
     * Downloads the specified report (docx, xlsx, or pdf) for a completed job.
     * It reads the manifest to find the correct report path.
     * @param jobId
     * @param format
     * @returns any Successful Response
     * @throws ApiError
     */
    public downloadReport(
        jobId: string,
        format: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/report/{format}',
            path: {
                'job_id': jobId,
                'format': format,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Target Detection Result
     * Returns the target.json file for the specified job from the StateStore.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getTargetDetectionResult(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/target',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
