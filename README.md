# aws-api-gateway-cognito
AWS API Gateway with lambdas functions and AWS Cognito

## Configuration

At first, you need to have the credetials for your AWS account in `~/.aws/credentials`.


Before you deploy the resources, you can modify the `config.json` file.

In this file you'll find some particular information about the deployment like the name of the service, the name of the Cognito User Pool, the region where you want to deploy it...

You should modify with your proper information.

## Deployment

You can now start the deployment into using the serverless command: `$> serverless deploy`.

## Test your API Gateway with Cognito

When the deployment is done, you can find in the AWS Console the different resources deployed such as API Gateway, Lambdas and Cognito.

If you want to test the authentification, you need to create a user into your Cognito User Pool and get a token for your user, that's why you have the `example-auth.json` file.

### Create a user

You have to connect to the AWS Console and go on Cognito -> User Pool -> Your User Pool (get and save your Pool Id) --> App Clients and click on `Show details` and click on `Enable username password auth for admin APIs for authentication (ALLOW_ADMIN_USER_PASSWORD_AUTH)` and Save app client changes. (get and save your App client Id too).

To create a user you have to launch the following command (replace the $ variables, and note that you will need to change the password):

`$> aws cognito-idp admin-create-user --user-pool-id $userPoolId --username $userName --temporary-password $userPassword`


You now have to modify the `example-auth.json` into replacing the different variables and do the following command to initiate your user:

`$> aws cognito-idp admin-initiate-auth --cli-input-json file://example-auth.json`

copy the value of `Session` in the output and do the following command to change the password (replace the $ variables):

`$> aws cognito-idp admin-respond-to-auth-challenge --user-pool-id $userPoolId --client-id $clientId --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses NEW_PASSWORD=$newPassword,USERNAME=$userName --session $session`


### Use your user to test endpoints which required authentification

Once you have your user created, initiated and with a new password (don't forget to change the password by the new password in the `example-auth.json` file) you can do the following command and get your token:

`$> aws cognito-idp admin-initiate-auth --cli-input-json file://example-auth.json`

In the output, the value of `tokenId` is your token and you can use it to make some requests to your endpoints (with Postman for example).
