def lambda_handler(event, context):
    #Implementation

    import urllib, json, sys, os, base64, boto3, botocore

    #Read in environment variables
    awsAccountId = os.environ["AwsAccountId"]
    roleArn = os.environ["RoleArn"]

    #Read in the values passed to Lambda function
    openIdToken = event['queryStringParameters']['openIdToken']
    dashboardId = event['queryStringParameters']['dashboardId']
    dashboardRegion = event['queryStringParameters']['dashboardRegion']
    resetDisabled = True
    undoRedoDisabled = True

    userName = json.loads(base64.b64decode(openIdToken.split('.')[1]+ "========"))['cognito:username']
    #Assume role that has permissions on QuickSight
    sts = boto3.client('sts')
    assumedRole = sts.assume_role_with_web_identity(
        RoleArn = roleArn,
        RoleSessionName = userName,
        WebIdentityToken = openIdToken
    )

    assumedRoleSession = boto3.Session(
            aws_access_key_id = assumedRole['Credentials']['AccessKeyId'],
            aws_secret_access_key = assumedRole['Credentials']['SecretAccessKey'],
            aws_session_token = assumedRole['Credentials']['SessionToken'],
        )

    quickSight = assumedRoleSession.client('quicksight',region_name= dashboardRegion)

    #Generate Embed url
    response = quickSight.get_dashboard_embed_url(
                    AwsAccountId = awsAccountId,
                    DashboardId = dashboardId,
                    IdentityType = 'IAM',
                    SessionLifetimeInMinutes = 600,
                    UndoRedoDisabled = undoRedoDisabled,
                    ResetDisabled = resetDisabled
                )

    return {
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps(response)
           }
