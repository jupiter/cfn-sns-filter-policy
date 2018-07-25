# cfn-sns-filter-policy
A CloudFormation custom resource for setting an SNS filter policy

## What

AWS [SNS](https://docs.aws.amazon.com/sns/latest/dg/welcome.html) allows for pub/sub message distribution to AWS Lambda, SQS, HTTP webhooks and more. SNS delivers published messages at least once (with retry on failure) to each subscriber.

Particularly useful features are:
- [Fan Out](https://docs.aws.amazon.com/sns/latest/dg/SNS_Scenarios.html) - multiple subscribers to one topic; and
- [Message filtering](https://docs.aws.amazon.com/sns/latest/dg/message-filtering.html) - selective delivery based on matching rules.

Although CloudFormation can be used to create subscriptions, for delivery to Lambda and SQS for example, there is no resource type for setting a filter policy on the subscription. Luckily there's something like [Custom Resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html), which lets us use a Lambda function to set/update/delete a policy on a subscription.

Note: The account deploying stacks including these custom resources will need to have invoke permission for the function. The account deploying the stack therefore effectively has permission to set a filter policy on *any* SNS subscription. As deployment account is unlikely to ever have more granular permissions, this should not be a problem.

## Installation

Using the [AWS CLI](https://aws.amazon.com/cli/), deploy the custom resource handler:

```
$ aws cloudformation deploy \
  --template-file ./custom_resource.yml \
  --capabilities CAPABILITY_IAM \
  --stack-name sns-filter-policy-custom-resource
```

## Example

We can use the custom resource in our template, see [example.yml](example.yml):

```yml
  MyExampleFilterPolicy:
    Type: Custom::SNSSetFilterPolicy
    Properties:
      ServiceToken: !ImportValue SNSSetFilterPolicyServiceToken
      Endpoint: !GetAtt MyExampleOutputQueue.Arn
      TopicArn: !Ref MyExampleTopic
      PolicyString: |-
        {
          "tag": ["rugby", "netball"]
        }
```

And deploy the example:

```
$ aws cloudformation deploy \
  --template-file ./example.yml \
  --capabilities CAPABILITY_IAM \
  --stack-name sns-filter-policy-example
```

To verify, get the `TopicArn` and `QueueUrl` outputs:

```
$ aws cloudformation describe-stacks \
  --stack-name sns-filter-policy-example
```

And publish some messages:

```
$ aws sns publish \
  --message Netball! \
  --topic-arn arn:aws:sns:...
  --message-attributes '{"tag":{"DataType": "String","StringValue": "netball"}}' \
  aws sns publish \
  --message Dodgeball! \
  --message-attributes '{"tag":{"DataType": "String","StringValue": "dodgeball"}}' \
  --topic-arn arn:aws:sns:...
  aws sns publish \
  --message Rugby! \
  --topic-arn arn:aws:sns:...
  --message-attributes '{"tag":{"DataType": "String","StringValue": "rugby"}}' \
```

You'll see how *only* messages matching our filter policy lands in the queue:

```
$ aws sqs receive-message \
  --visibility-timeout 60 \
  --wait-time-seconds 10 \
  --max-number-of-messages 10 \
  --queue-url https://sqs....
```

(You may need to repeat this a few times.)
