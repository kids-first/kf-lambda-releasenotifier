Kids First Release Notifier
===========================

A lambda to send SNS messages from the Release Coordinator to slack.


Configuration
-------------

The lambda needs to be configured with the correct variables in the environment
to be able to send messages to slack:

- `SLACK_TOKEN` - Token provided by slack for API use
- `SLACK_CHANNEL` - The channel that notifications will be sent to
- `COORDINATOR_URL` - The url of the Release Coordinator api
