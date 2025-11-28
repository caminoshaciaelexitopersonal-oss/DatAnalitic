/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnonymizeRequest } from '../models/AnonymizeRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MpaComplianceService {
    /**
     * Anonymize Data
     * Anonymizes PII data for a given session.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static anonymizeDataUnifiedV1MpaComplianceAnonymizePost(
        requestBody: AnonymizeRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
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
