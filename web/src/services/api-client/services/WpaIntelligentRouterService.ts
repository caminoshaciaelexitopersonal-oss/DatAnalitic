/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WpaIntelligentRouterService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Intelligent Predict
     * Dynamically selects the best model from the scoreboard, loads it,
     * and performs a prediction.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public intelligentPredictUnifiedV1WpaRouterPredictPost(
        requestBody: Array<Record<string, any>>,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
