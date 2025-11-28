/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubmitRequest } from '../models/SubmitRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WpaAutomatedAnalysisService {
    /**
     * Submit Auto Analysis Job
 
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static submitAutoAnalysisJobUnifiedV1WpaAutoAnalysisSubmitPost(
        requestBody: SubmitRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/auto-analysis/submit',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Status
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getJobStatusUnifiedV1WpaAutoAnalysisJobIdStatusGet(
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
    public static getGeneratedCodeUnifiedV1WpaAutoAnalysisJobIdCodeGet(
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
     * Download Docx Report
     * Generates and serves a DOCX report for the completed analysis job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadDocxReportUnifiedV1WpaAutoAnalysisJobIdReportDocxGet(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/report/docx',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Excel Report
     * Generates and serves an Excel report for the completed analysis job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadExcelReportUnifiedV1WpaAutoAnalysisJobIdReportExcelGet(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/report/excel',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Pdf Report
     * Generates and serves a PDF report for the completed analysis job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadPdfReportUnifiedV1WpaAutoAnalysisJobIdReportPdfGet(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-analysis/{job_id}/report/pdf',
 
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
