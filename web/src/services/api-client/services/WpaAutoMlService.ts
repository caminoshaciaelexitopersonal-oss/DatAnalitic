/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AutoMLRequest } from '../models/AutoMLRequest';
import type { AutoMLSubmitResponse } from '../models/AutoMLSubmitResponse';
import type { HPORequest } from '../models/HPORequest';
import type { HPOSubmitResponse } from '../models/HPOSubmitResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WpaAutoMlService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Automl Status
     * Returns the status of the AutoML module, including the number of registered models.
     * @returns any Successful Response
     * @throws ApiError
     */
    public getAutoMlStatus(): CancelablePromise<any> {
        return this.httpRequest.request({
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
    public getAutoMlModels(): CancelablePromise<any> {
        return this.httpRequest.request({
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
    public downloadAutoMlModel(
        jobId: string,
        modelName: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
    public submitAutoMlJob(
        requestBody: AutoMLRequest,
    ): CancelablePromise<AutoMLSubmitResponse> {
        return this.httpRequest.request({
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
    public submitHpoJob(
        requestBody: HPORequest,
    ): CancelablePromise<HPOSubmitResponse> {
        return this.httpRequest.request({
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
