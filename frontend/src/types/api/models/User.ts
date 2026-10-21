/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Public representation of the authenticated user.
 */
export type User = {
    readonly id: number;
    /**
     * Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
     */
    readonly username: string;
    readonly email: string;
    readonly first_name: string;
    readonly last_name: string;
};

