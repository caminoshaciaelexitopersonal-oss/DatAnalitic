/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnonymizeRequest } from '../models/AnonymizeRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaComplianceService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Anonymize Data
     * Anonymizes PII data for a given session.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public anonymizeDataUnifiedV1MpaComplianceAnonymizePost(
        requestBody: AnonymizeRequest,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/unified/v1/mpa/compliance/anonymize',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
