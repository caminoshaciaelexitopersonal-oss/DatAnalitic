/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_createJobUnified } from '../models/Body_createJobUnified';
import type { Job } from '../models/Job';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class McpMainControlPlaneService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Create Job Unified
     * Unified endpoint to start a new analysis job.
     * 1. Creates a Session and a Job.
     * 2. Uploads the data file to object storage (MinIO).
     * 3. Triggers the master asynchronous pipeline.
     * @param formData
     * @returns Job Successful Response
     * @throws ApiError
     */
    public createJobUnified(
        formData: Body_createJobUnified,
    ): CancelablePromise<Job> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/unified/v1/mcp/job/start',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Status Unified
     * Retrieves the current status of a job.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getJobStatusUnified(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/mcp/job/{job_id}/status',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Results
     * Retrieves a consolidated summary of the job results from the StateStore for the frontend.
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getJobResults(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/mcp/job/{job_id}/results',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
