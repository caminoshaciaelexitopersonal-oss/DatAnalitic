/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_file_unified_v1_mpa_ingestion_upload_file__post } from '../models/Body_upload_file_unified_v1_mpa_ingestion_upload_file__post';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MpaIngestionService {
    /**
     * Upload File
     * Handles file uploads and processes them using the IngestionService.
     * This is the new MPA-based endpoint for file ingestion.
     * **Requires DATA_SCIENTIST role.**
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static uploadFileUnifiedV1MpaIngestionUploadFilePost(
        formData: Body_upload_file_unified_v1_mpa_ingestion_upload_file__post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
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
