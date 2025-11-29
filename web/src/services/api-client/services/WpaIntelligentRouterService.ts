/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WpaIntelligentRouterService {
    /**
     * Intelligent Predict
     * Dynamically selects the best model from the scoreboard, loads it,
     * and performs a prediction.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static intelligentPredictUnifiedV1WpaRouterPredictPost(
        requestBody: Array<Record<string, any>>,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/router/predict',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
