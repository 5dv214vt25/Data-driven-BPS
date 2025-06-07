
/**
 * Represents the user authentication object we use store user data in. 
 * 
 */
export interface iAuthentication {
    /**
     * holds the user username/email-address
     */
    username: string;
    /**
     * holds the user password
     */
    password: string;
    /**
     * a boolean value to check if user should have access or not.
     */
    authorized: boolean;
}
