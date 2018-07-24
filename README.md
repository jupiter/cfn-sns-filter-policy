# cfn-sns-filter-policy
A Cloudformation custom resource for setting an SNS filter policy

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
    Type: Custom::SNSSubscriptionFilterPolicy
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
  --message-attributes '{"tag":{"DataType": "String","StringValue": "rugby"}}' \
  --topic-arn arn:aws:sns:...
  aws sns publish \
  --message Dodgeball! \
  --message-attributes '{"tag":{"DataType": "String","StringValue": "dodgeball"}}' \
  --topic-arn arn:aws:sns:...
  aws sns publish \
  --message Rugby! \
  --message-attributes '{"tag":{"DataType": "String","StringValue": "netball"}}' \
  --topic-arn arn:aws:sns:...
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
