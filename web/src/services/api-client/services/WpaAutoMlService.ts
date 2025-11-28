/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WpaAutoMlService {
    /**
     * Submit Automl Job
     * @returns any Successful Response
     * @throws ApiError
     */
    public static submitAutomlJobUnifiedV1WpaAutoMlSubmitPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/auto-ml/submit',
        });
    }
    /**
     * Get Job Status
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getJobStatusUnifiedV1WpaAutoMlJobIdStatusGet(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-ml/{job_id}/status',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Models
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getJobModelsUnifiedV1WpaAutoMlJobIdModelsGet(
        jobId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-ml/{job_id}/models',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Model
     * @param jobId
     * @param modelName
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadModelUnifiedV1WpaAutoMlJobIdDownloadModelNameGet(
        jobId: string,
        modelName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-ml/{job_id}/download/{model_name}',
            path: {
                'job_id': jobId,
                'model_name': modelName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
