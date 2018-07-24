import json
import boto3
from botocore.exceptions import ClientError
from urllib.request import build_opener, HTTPHandler, Request

client = boto3.client('sns')

def send_response(event, responseStatus, reason, responseData):
    responseBody = json.dumps({
        "Status": responseStatus,
        "Reason": reason,
        "PhysicalResourceId": event['ServiceToken'],
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": responseData
    }).encode("utf-8")
    print(responseBody)
    opener = build_opener(HTTPHandler)
    request = Request(event['ResponseURL'], data=responseBody)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(responseBody))
    request.get_method = lambda: 'PUT'
    response = opener.open(request)

def get_subscription_arn(topic_arn, endpoint):
    next_token = ""
    while next_token != None:
        response = client.list_subscriptions_by_topic(
            TopicArn=topic_arn,
            NextToken=next_token
        )
        subs = response.get('Subscriptions', [])
        found = [x for x in subs if x['Endpoint'] == endpoint]
        if found:
            return found[0]['SubscriptionArn']
        next_token = response.get("NextToken", None)
    return None

def handler(event, context):
    properties = event["ResourceProperties"]
    topic_arn = properties.get("TopicArn", "")
    endpoint = properties.get("Endpoint", "")
    policy_string = properties.get("PolicyString", "")
    if event["RequestType"] == "Delete":
        policy_string = '{}'
    try:
        subscription_arn = get_subscription_arn(topic_arn, endpoint)
        response = client.set_subscription_attributes(
            SubscriptionArn=subscription_arn,
            AttributeName="FilterPolicy",
            AttributeValue=policy_string
        )
    except ClientError as e:
        reason = e.response['Error']['Message']
        send_response(event, "FAILURE", reason, {})
        return
    send_response(event, "SUCCESS", "No errors", {})
