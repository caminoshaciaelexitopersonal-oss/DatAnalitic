/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WpaAutomatedAnalysisService {
    /**
     * Get All Job Statuses
     * Returns the status of all jobs.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAllJobStatuses(): CancelablePromise<any> {
        return __request(OpenAPI, {
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
    public static getJobStatus(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * Get Generated Code
     * Returns the code generated during the analysis in the specified format.
     * @param jobId
     * @param format
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getGeneratedCode(
        jobId: string,
        format: string = 'python',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/code',
            path: {
                'job_id': jobId,
            },
            query: {
                'format': format,
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
    public static downloadReport(
        jobId: string,
        format: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * Returns the target.json file for the specified job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTargetDetectionResult(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
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
