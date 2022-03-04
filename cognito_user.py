#!/usr/bin/env python3
import argparse
import boto3
import botocore.credentials
import botocore.exceptions
import botocore.client
import logging
import random
import string
from getpass import getpass


def get_random_password(size):
    random_source = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)

    for i in range(size - 4):
        password += random.choice(random_source)

    password_list = list(password)
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password


def authenticate_user(client, username, password, user_pool_id, client_id):
    try:
        response = client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            }
        )
        return response['AuthenticationResult']['IdToken']
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            logging.error("%s user not found", username)
        else:
            logging.error("error while authenticating user: %s", e)


def create_user(client, username, password, user_pool_id, client_id):
    try:
        temporary_password = get_random_password(16)
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=temporary_password
        )
        auth = client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': temporary_password,
            }
        )
        response = client.admin_respond_to_auth_challenge(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses={'NEW_PASSWORD': password, 'USERNAME': username},
            Session=auth['Session'],
        )
        return response['AuthenticationResult']['IdToken']
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            logging.error("%s user already exists", username)
        else:
            logging.error("error while creating and responding to auth challenge: %s", e)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Create or authenticate users and get token id "
                    "to help you quickly test your cognito pools and apps."
    )
    parser.add_argument("username", type=str)
    parser.add_argument("user_pool_id", type=str, help="The cognito user pool id")
    parser.add_argument("client_id", type=str, help="The cognito user pool client id")
    parser.add_argument("--profile", type=str, default="default", help="AWS Profile to use. Default: default")
    parser.add_argument("--region", type=str, default="us-west-2",
                        help="Region where your user pool is. Default: us-west-2")
    parser.add_argument("--create", dest="create", action="store_true",
                        help="Create user, respond to cognito challenge and authenticate user. "
                             "If this argument is not given it will only authenticate the user")
    parser.set_defaults(feature=False)
    args = parser.parse_args()
    return args


def cognito_user():
    args = parse_arguments()
    logging.basicConfig(format="%(asctime)s %(message)s", datefmt="[%I:%M:%S %p]", level=logging.INFO)
    try:
        password = getpass("User password:")
        session = boto3.session.Session(profile_name=args.profile, region_name=args.region)
        client = session.client("cognito-idp")
        if args.create:
            token = create_user(client, args.username, password, args.user_pool_id, args.client_id)
            logging.info("Token: %s", token)
        else:
            token = authenticate_user(client, args.username, password, args.user_pool_id, args.client_id)
            logging.info("Token: %s", token)
    except Exception as e:
        logging.error("error while processing: %s", e)


if __name__ == '__main__':
    cognito_user()
