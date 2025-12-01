/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_loginForAccessToken } from '../models/Body_loginForAccessToken';
import type { Token } from '../models/Token';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuthenticationService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Login For Access Token
     * Provides a JWT token for valid user credentials.
     * @param formData
     * @returns Token Successful Response
     * @throws ApiError
     */
    public loginForAccessToken(
        formData: Body_loginForAccessToken,
    ): CancelablePromise<Token> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/auth/token',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
