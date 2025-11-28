/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_create_job_unified_v1_mcp_job_start_post } from '../models/Body_create_job_unified_v1_mcp_job_start_post';
import type { Body_create_step_unified_v1_mcp_step_post } from '../models/Body_create_step_unified_v1_mcp_step_post';
import type { Job } from '../models/Job';
import type { Session } from '../models/Session';
import type { Step } from '../models/Step';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class McpMainControlPlaneService {
    /**
     * Create Session
     * Creates a new analysis session.
     * @returns Session Successful Response
     * @throws ApiError
     */
    public static createSessionUnifiedV1McpSessionCreatePost(): CancelablePromise<Session> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mcp/session/create',
        });
    }
    /**
     * Get Session
     * Retrieves a session by its ID.
     * @param sessionId
     * @returns Session Successful Response
     * @throws ApiError
     */
    public static getSessionUnifiedV1McpSessionSessionIdGet(
        sessionId: string,
    ): CancelablePromise<Session> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/mcp/session/{session_id}',
            path: {
                'session_id': sessionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Job
     * Creates a new job within a session.
     * @param requestBody
     * @returns Job Successful Response
     * @throws ApiError
     */
    public static createJobUnifiedV1McpJobStartPost(
        requestBody: Body_create_job_unified_v1_mcp_job_start_post,
    ): CancelablePromise<Job> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mcp/job/start',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Step
     * Creates a new step within a job.
     * @param requestBody
     * @returns Step Successful Response
     * @throws ApiError
     */
    public static createStepUnifiedV1McpStepPost(
        requestBody: Body_create_step_unified_v1_mcp_step_post,
    ): CancelablePromise<Step> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/mcp/step',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
