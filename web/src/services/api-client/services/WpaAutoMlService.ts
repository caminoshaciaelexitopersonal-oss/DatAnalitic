/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AutoMLRequest } from '../models/AutoMLRequest';
import type { AutoMLSubmitResponse } from '../models/AutoMLSubmitResponse';
import type { HPORequest } from '../models/HPORequest';
import type { HPOSubmitResponse } from '../models/HPOSubmitResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WpaAutoMlService {
    /**
     * Get Automl Status
     * Returns the status of the AutoML module, including the number of registered models.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAutoMlStatus(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-ml/status',
        });
    }
    /**
     * Get Automl Models
     * Returns a list of all registered models.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAutoMlModels(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-ml/models',
        });
    }
    /**
     * Download Automl Model
     * Downloads a trained model.
     * @param jobId
     * @param modelName
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadAutoMlModel(
        jobId: string,
        modelName: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/auto-ml/download/{job_id}/{model_name}',
            path: {
                'job_id': jobId,
                'model_name': modelName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Submit Automl Job
     * Submits a new AutoML job.
     * This enqueues a Celery task to run the full AutoML pipeline.
     * @param requestBody
     * @returns AutoMLSubmitResponse Successful Response
     * @throws ApiError
     */
    public static submitAutoMlJob(
        requestBody: AutoMLRequest,
    ): CancelablePromise<AutoMLSubmitResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/auto-ml/submit',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Submit Hpo Job
     * Submits a new HPO job.
     * @param requestBody
     * @returns HPOSubmitResponse Successful Response
     * @throws ApiError
     */
    public static submitHpoJob(
        requestBody: HPORequest,
    ): CancelablePromise<HPOSubmitResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/auto-ml/hpo/submit',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
