# Spec Delta

## Purpose

Lets users communicate with each other through conversations and the messages they exchange in them, to help develop ideas.

## ADDED Requirements

### Requirement: Retain sent messages with their conversation and sender
The system SHALL retain each non-empty message with a reference to the conversation it belongs to, an optional reference to the user who sent it, its text, and the time it was sent. If the sender's account is deleted, the message remains and its sender reference becomes empty.

Source: US029 (#100)

#### Scenario: Non-empty message is recorded in a conversation
- **WHEN** the later sending flow saves a non-empty message sent by a user who has opened a conversation with another user
- **THEN** the message record contains the sent text, identifies its conversation and sender, and records the time it was sent

#### Scenario: Message survives deletion of its sender
- **WHEN** a conversation contains a message and the sender's account is deleted
- **THEN** the message is still retained in the conversation and has no sender reference

### Requirement: Reject messages with empty text
The system SHALL treat a message with empty text as invalid so that it is not accepted as a message record.

Source: US029 (#100)

#### Scenario: Empty message fails validation
- **WHEN** a user in a conversation tries to save a message whose text is empty
- **THEN** the message is reported as invalid because its text is required

### Requirement: Return conversation messages in chronological order
The system SHALL return the messages of a conversation ordered from the earliest sent to the latest sent, each with its sender information.

Source: US029 (#100)

#### Scenario: Messages come back oldest first
- **WHEN** a conversation contains messages sent at different times and its messages are retrieved
- **THEN** the messages are returned in the order they were sent, oldest first, and each identifies its sender
