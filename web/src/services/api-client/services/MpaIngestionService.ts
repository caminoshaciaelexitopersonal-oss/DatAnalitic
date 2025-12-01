/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_uploadFile } from '../models/Body_uploadFile';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaIngestionService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Upload File
     * Handles file uploads and processes them using the IngestionService.
     * This is the new MPA-based endpoint for file ingestion.
     * **Requires DATA_SCIENTIST role.**
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public uploadFile(
        formData: Body_uploadFile,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/unified/v1/mpa/ingestion/upload-file/',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
